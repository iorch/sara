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
import elasticsearch


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


def get_relevant_hits(like_text):
    index_name = "peticion"
    doc_type = "pregunta"
    stop_words = ["para","apoyo","una","la","el","de","en"]
    body = {"query": { "more_like_this" : { "fields":["titulo"],
            "like_text" : like_text, "min_term_freq" : 1, 
            "max_query_terms" : 100, "min_doc_freq": 0,
            "stop_words":stop_words}}}
    es = elasticsearch.Elasticsearch()
    mlts = es.search(index=index_name, doc_type=doc_type,body=body)
    relevant_sugestions = []                    
    hits = mlts.get('hits')["hits"]
    for hit in hits:
        if hit["_score"] >= 0.5:
            source = hit["_source"]
            relevant_sugestions.append({"title": source["titulo"],
            "description": source["sugerencia"], "link": source["link"]})
    return relevant_sugestions
    

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
def create_task():
    if not request.json or not 'id' in request.json:
        abort(400)
    task = {
        'id': request.json['id'],
        'title': request.json['title'],
        'description': request.json['description'],
    }
    clean_test_descripciones = []
    features = review_words(task['description'])
    clean_test_descripciones.append(u" ".join(
        KaggleWord2VecUtility.review_to_wordlist(features, True))
        )
    myeval = evaluate_petition(clean_test_descripciones)
    # tasks.append(task)
    return jsonify({'id': request.json['id'],
                    'title': request.json['title'],
                    'description': request.json['description'],
                    'classification_id': myeval[0]}), 201


@app.route('/recommendations', methods=['GET'])
def get_hits():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'title': request.json['title']
    }
    relevant_sugestions = get_relevant_hits(task['title'])
    return jsonify({'results': relevant_sugestions})
    
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
