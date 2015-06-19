# Celery tasks

from celery import Celery
from sklearn.externals import joblib

BROKER_URL = 'redis://localhost:6379/0'
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 1800}  # 1/2 hour.
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

app = Celery('tasks', backend=CELERY_RESULT_BACKEND, broker=BROKER_URL)


@app.task
def evaluate_petition(features):
    pipe = joblib.load('models/bow_ng6_nf9500_ne750.pkl')
    test_data_features = pipe.named_steps['vectorizer'].transform(features)
    test_data_features = test_data_features.toarray()
    result = pipe.named_steps['forest'].predict(test_data_features)
    print result
    return result


