import os
from datetime import timedelta
from pathlib import Path

from flask import Flask, jsonify
from flask_jwt import JWT, JWTError
from flask_restful import Api

# Import my Restful api resources
from resources.item import ItemResource, ItemListResource
from resources.store import StoreResource, StoreListResource
from resources.user import UserRegister
from security import authenticate, identity as identity_function

# Creating our flask app and configure it through its config dictionary
flaskApp = Flask(__name__)

# Use 12factor inspired environment variables or from a file
import environ

# Create a local.env file in the settings directory
# But ideally this env file should be outside the git repo
env_file = Path(__file__).resolve().parent / 'local.env'
if env_file.exists():
    environ.Env.read_env(str(env_file))

env = environ.Env()

flaskApp.config['DEBUG'] = env('FLASK_DEBUG', default=True)
flaskApp.config['ENV'] = env('FLASK_ENV', default='development')  # same as: os.environ['FLASK_ENV'] = True

if flaskApp.config['ENV'] == 'development':
    default_db_uri = 'sqlite:///data.db'
else:
    default_db_uri = 'postgresql://test:test@localhost:5432/store'

flaskApp.config['SQLALCHEMY_DATABASE_URI'] = env('DATABASE_URL', default=default_db_uri)
flaskApp.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# flaskApp.config['PROPAGATE_EXCEPTIONS'] = True

# SECURITY WARNING: keep the secret key used in production secret!
# Raises ImproperlyConfigured exception if SECRET_KEY not in os.environ
flaskApp.secret_key = env('SECRET_KEY')

# Creating our Restful Flask Api
flaskApp.config['BASE_API_URL'] = '/api'
api = Api(flaskApp)

# Token expiration time for our JWT environment
# config JWT to expire within half an hour
flaskApp.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=1800)

# The jwt object takes or flask app, the authentication and identity handlers and link them all.
jwt = JWT(flaskApp, authenticate,
          identity_function)  # Calling /auth we'll use Flask-JWT to authenticate users and validate token.

# Adding restful resources
api.add_resource(ItemResource, flaskApp.config['BASE_API_URL'] + '/item/<string:name>')
api.add_resource(StoreResource, flaskApp.config['BASE_API_URL'] + '/store/<string:name>')
api.add_resource(ItemListResource, flaskApp.config['BASE_API_URL'] + '/items')
api.add_resource(StoreListResource, flaskApp.config['BASE_API_URL'] + '/stores')

api.add_resource(UserRegister, flaskApp.config['BASE_API_URL'] + '/register')


@flaskApp.route('/')
def home():
    return jsonify({'message': 'hello world'})


# customize JWT auth response, include user_id in response body
# Remember that the identity should be what you've returned by the authenticate()
# function, and in our sample, it is a UserModel object which contains a field id. Make
# sure to only access valid fields in your identity model!
@jwt.auth_response_handler
def customized_response_handler(access_token, identity):
    return jsonify({
        'access_token': access_token.decode('utf-8'),
        'user_id': identity.id
    })


@flaskApp.errorhandler(JWTError)
def errorHandler(error):
    """
    This decorated function is going to handle all the JWTError exceptions generated when an authentication token
    is mandatory in order to use our endpoints
    :param error:
    :return:
    """
    return jsonify({"message": "We could not authorize. Did you include the valid authorization header?"}), 401


if __name__ == "__main__":
    from db import db

    db.init_app(flaskApp)

    if flaskApp.config['DEBUG']:
        @flaskApp.before_first_request
        def create_all_tables():
            db.create_all()

    flaskApp.run(port=5000)
