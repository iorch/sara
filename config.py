import os
import logging

class BaseConfig(object):
    DEBUG = os.getenv('DEBUG_MODE')
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_URL')
    LOGLEVEL = logging.DEBUG
    LOGFILE = '/logs/sara.log'



class TestConfig(BaseConfig):
    LOGLEVEL = logging.DEBUG

class StagingConfig(BaseConfig):
    LOGFILE = '/logs/stagingapp.log'

