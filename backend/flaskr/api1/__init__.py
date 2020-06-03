from flask import Blueprint
from flask_cors import CORS

# initializing the blueprint
api1 = Blueprint('api1', __name__)
CORS(api1, resources={r'/api/*': {'origins': '*'}})
from . import routes
