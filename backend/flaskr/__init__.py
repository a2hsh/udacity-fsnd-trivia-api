import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Instantiating global objects and variables
QUESTIONS_PER_PAGE = 10
db = SQLAlchemy()
cors = CORS()

def create_app(config=None):
  # create and configure the app
  app = Flask(__name__)
  if config == 'development':
    app.config.from_object('config.DevConfig')
  elif config == 'production':
    app.config.from_object('config.ProdConfig')
  elif config == 'testing':
    app.config.from_object('config.TestConfig')
  else:
    raise EnvironmentError('Please specify a configuration profile for the application')
  db.init_app(app)
  cors.init_app(app, resources={'/': {'origins': '*'}})
  with app.app_context():
    from . import routes
    db.create_all()


  return app

    