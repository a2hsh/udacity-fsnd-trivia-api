"""Flask configuration file"""
from os import environ, path
from dotenv import load_dotenv
basedir = path.abspath(path.dirname(__file__))
# load environment variables file
load_dotenv(path.join(basedir, '.env'))


class Config:
    """Base config"""
    SECRET_KEY = environ.get('SECRET_KEY') or 'HackMePleaseLol'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    QUESTIONS_PER_PAGE = 10


class ProdConfig(Config):
    """ production config"""
    ENV = 'production'
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = environ.get('PROD_DATABASE_URI')


class DevConfig(Config):
    """development config"""
    ENV = 'development'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = environ.get('DEV_DATABASE_URI')


class TestConfig(DevConfig):
    """testing config"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = environ.get('TEST_DATABASE_URI')
