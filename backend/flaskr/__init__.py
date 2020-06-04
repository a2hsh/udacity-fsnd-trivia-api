import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

# Instantiating global objects and variables
db = SQLAlchemy()


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
        raise EnvironmentError(
            'Please specify a valid configuration profile for the application. Possible choices are `development`, `testing`, or `production`')
    # initializing application extentions
    db.init_app(app)
    # bind all extentions to the app instance
    with app.app_context():
        # import blueprints
        from .api1 import api1
        # register blueprints
        app.register_blueprint(api1, url_prefix='/api/v1')
        # create all tables in the database
        db.create_all()

        # force 404 and 405 errors to return a json object if requested from the api blueprint
        @app.errorhandler(404)
        def _handle_404(error):
            if request.path.startswith('/api/v1/'):
                return jsonify({
                    'success': False,
                    'error': 404,
                    'message': 'resource not found'
                }), 404
            else:
                return error

        @app.errorhandler(405)
        def _handle_405(error):
            if request.path.startswith('/api/v1/'):
                return jsonify({
                    'success': False,
                    'error': 405,
                    'message': 'method not allowed'
                }), 405
            else:
                return error
    return app
