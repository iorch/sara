#!/usr/bin/env python
# coding=utf-8

from flask import Flask, request, jsonify, make_response, abort
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.externals import joblib
from bs4 import BeautifulSoup
import re
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'DeepLearningMovies/'))
from KaggleWord2VecUtility import KaggleWord2VecUtility
sys.path.append(os.path.dirname(__file__))
from profanity_filter import *
from nltk.corpus import stopwords


app = Flask(__name__)


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


def evaluate_petition(features):
    pipe = joblib.load('models/bow_ng6_nf9500_ne750.pkl')
    test_data_features = pipe.named_steps['vectorizer'].transform(features)
    test_data_features = test_data_features.toarray()
    result = pipe.named_steps['forest'].predict(test_data_features)
    return result


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


@app.route('/sac/peticiones/clasificador', methods=['POST'])
def create_task():
    if not request.json or not 'folioSAC' in request.json:
        abort(400)
    task = {
        'folioSAC': request.json['folioSAC'],
        'descripcion': request.json['descripcion'],
    }
    clean_test_descripciones = []
    features = review_words(task['descripcion'])
    clean_test_descripciones.append(u" ".join(
        KaggleWord2VecUtility.review_to_wordlist(features, True))
        )
    myeval = evaluate_petition(clean_test_descripciones)
    # tasks.append(task)
    return jsonify({'dependencia_sugerida': myeval[0]}), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
