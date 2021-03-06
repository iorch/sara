#!/usr/bin/env python
# coding=utf-8

from flask import Flask, request, jsonify, make_response, abort, g
from flask_sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from bs4 import BeautifulSoup
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'DeepLearningMovies/'))
from KaggleWord2VecUtility import KaggleWord2VecUtility
sys.path.append(os.path.dirname(__file__))
from profanity_filter import *
from recommendations import *
from nltk.corpus import stopwords
from tasks import evaluate_petition
from tasks import catch_bad_words_in_text
from tasks import update_remote_petition
from celery import chord
import json

from logging.handlers import RotatingFileHandler

# download stop words
import nltk
nltk.download('stopwords')

app = Flask(__name__)

config_class = 'config.BaseConfig'
if os.getenv('STAGING'):
    config_class = 'config.StagingConfig'
app.config.from_object(config_class)

handler = RotatingFileHandler(app.config['LOGFILE'], maxBytes=150*1024*1024, backupCount=5)
handler.setLevel(app.config['LOGLEVEL'])
app.logger.addHandler(handler)


db = SQLAlchemy(app)
auth = HTTPBasicAuth()

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user = User.query.get(data['id'])
        return user


@auth.verify_password
def verify_password(username_or_token, password):
    user = User.verify_auth_token(username_or_token)
    if not user:
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)
    if User.query.filter_by(username=username).first() is not None:
        abort(400)
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'username': user.username}), 201)


@app.route('/users/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


def review_words(raw_text):
    review_text = BeautifulSoup(raw_text).get_text()
    letters_only = re.sub("^(\w+)[0-9]@", "", review_text)
    callback = lambda pat: pat.group(0).decode('utf-8').lower()
    iac = re.sub(u"Ă", u"í", letters_only)
    ene = re.sub(u"Ñ", u"ñ", iac)
    words = re.sub("(\w+)", callback, ene).split()
    stops = set(stopwords.words("spanish"))
    meaningful_words = [w for w in words if w not in stops]
    return u" ".join(meaningful_words)


@app.errorhandler(400)
def bad_request(error):
    app.logger.error(error)
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@app.errorhandler(404)
def not_found(error):
    app.logger.error(error)
    return make_response(jsonify({'error': 'Not Found'}), 404)


@app.route('/sac/peticiones/filtro_malas_palabras', methods=['POST'])
def filtro_malas_palabras():
    f = ProfanitiesFilter(my_list, replacements="-")
    if not request.json or not 'descripcion' in request.json:
        abort(400)
    task = {
        'folioSAC': request.json['folioSAC'],
        'descripcion': request.json['descripcion'],
    }
    profanity_score = f.profanity_score(task['descripcion'])
    return jsonify({'indice_de_groserias': profanity_score})


@app.route('/petition/classification', methods=['POST'])
@auth.login_required
def create_task():
    if not request.json or not 'id' in request.json:
        abort(400)
    task = {
        'id': request.json['id'],
        'text': request.json['text'],
    }
    clean_test_descripciones = []
    app.logger.info('petition_classification: ' + task['text'])
    features = review_words(task['text'])
    clean_test_descripciones.append(u" ".join(
        KaggleWord2VecUtility.review_to_wordlist(features, True)))

    # Uses chord to run two jobs and a callback after processing ends
    # 1) A text classifier
    # 2) A profanity filter
    # 3) A callback to put all together in a JSON
    callback = update_remote_petition.subtask()
    chord([
        evaluate_petition.s(task['id'], clean_test_descripciones),
        catch_bad_words_in_text.s(task['text'])
    ])(callback)

    return jsonify({'id': request.json['id'],
                    'text': request.json['text']}), 201


@app.route('/recommendations', methods=['GET'])
def get_hits():
    if not request.args.get('title', '') and (not request.json or not 'title' in request.json):
        abort(400)
    title = request.args.get('title', '') if request.args.get('title', '') else request.json['title']
    app.logger.info('petition_recommendations: ' + title)
    r = Recommender()
    relevant_sugestions = r.get_relevant_hits(title, 'peticion')
    relevant_sugestions += r.get_relevant_hits(title, 'formalities')
    return json.dumps({'results': relevant_sugestions}, encoding='utf-8', ensure_ascii=False)


if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(host='0.0.0.0')
