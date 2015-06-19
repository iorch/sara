#!/usr/bin/env python
# coding=utf-8
# Celery tasks

import os
from celery import Celery
from sklearn.externals import joblib

REDIS_HOST = os.getenv( 'REDIS_PORT_6379_TCP_ADDR', 'localhost' )+':'+os.getenv( 'REDIS_PORT_6379_TCP_PORT', '6379' )
BROKER_URL = 'redis://'+ REDIS_HOST +'/0'
CELERY_RESULT_BACKEND = 'redis://'+ REDIS_HOST +'/0'
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 1800}  # 1/2 hour.

app = Celery('tasks', backend=CELERY_RESULT_BACKEND, broker=BROKER_URL)


@app.task
def evaluate_petition(features):
    pipe = joblib.load('models/bow_ng6_nf9500_ne750.pkl')
    test_data_features = pipe.named_steps['vectorizer'].transform(features)
    test_data_features = test_data_features.toarray()
    result = pipe.named_steps['forest'].predict(test_data_features)
    print result
    return result


