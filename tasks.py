# Celery tasks
# -*- coding: utf-8 -*-

from celery import Celery
from sklearn.externals import joblib
from profanity_filter import *
import requests
import os

BROKER_URL = 'redis://localhost:6379/0'
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 1800}  # 1/2 hour.
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

app = Celery('tasks', backend=CELERY_RESULT_BACKEND, broker=BROKER_URL)


@app.task
def evaluate_petition(petition_id, features):
    pipe = joblib.load('models/bow_ng6_nf9500_ne750.pkl')
    test_data_features = pipe.named_steps['vectorizer'].transform(features)
    test_data_features = test_data_features.toarray()
    # TODO: check API of this method, what's returning on error?
    result = pipe.named_steps['forest'].predict(test_data_features)
    return {
        'id': petition_id,
        'agency': result[0] if len(result) > 0 else -1
    }


@app.task
def catch_bad_words_in_text(text):
    f = ProfanitiesFilter(my_list, replacements="-")
    # TODO: check API of this method, what's returning on error?
    profanity_score = f.profanity_score(text)
    return {
        'text': text,
        'profanity_score': profanity_score
    }


@app.task
def update_remote_petition(results):
    classified_petition = results[0]
    inspected_text = results[1]
    if inspected_text['profanity_score'] > 0:
        proceeds = {'value': False, 'reason': u'Petición Irrespetuosa'.encode('utf-8')}
    else:
        proceeds = {'value': True}

    petition = {
        'id': classified_petition['id'],
        'text': inspected_text['text'],
        'agency': classified_petition['agency'],
        'proceeds': proceeds
    }

    url = os.environ['PETITIONS_SERVER_URL']
    r = requests.put(url, data=petition)
    print 'Updating:'
    print petition
    print 'PUT request to', url, ' was ', r.status_code


