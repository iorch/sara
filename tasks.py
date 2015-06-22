# Celery tasks

from celery import Celery
from sklearn.externals import joblib
from profanity_filter import *
import json

BROKER_URL = 'redis://localhost:6379/0'
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 1800}  # 1/2 hour.
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

app = Celery('tasks', backend=CELERY_RESULT_BACKEND, broker=BROKER_URL)


@app.task
def evaluate_petition(features):
    pipe = joblib.load('models/bow_ng6_nf9500_ne750.pkl')
    test_data_features = pipe.named_steps['vectorizer'].transform(features)
    test_data_features = test_data_features.toarray()
    # TODO: check API of this method, what's returning on error?
    result = pipe.named_steps['forest'].predict(test_data_features)
    if len(result) > 0:
        return result[0]
    else:
        return -1


@app.task
def catch_bad_words_in_text(text):
    f = ProfanitiesFilter(my_list, replacements="-")
    # TODO: check API of this method, what's returning on error?
    profanity_score = f.profanity_score(text)
    return profanity_score


@app.task
def build_classification_response(results):
    profanity_score = results[1]
    proceeds = False if profanity_score > 0 else True

    response = {
            'agency': results[0],
            'proceeds': proceeds
            }
    print json.dumps(response)


