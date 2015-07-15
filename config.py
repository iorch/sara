import os


class Config(object):
    DEBUG = os.getenv('DEBUG_MODE')
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_URL')
