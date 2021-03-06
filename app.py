# -*- coding: utf-8 -*-
"""
Module app.py
~~~~~~~~~~~~
This module provides the flaskApp object for running the Flask application
"""

# Use 12factor inspired environment variables or from a file
import argparse
import os
from pathlib import Path

from flasgger import Swagger
from flask import Flask, abort
from flask_jwt_extended import JWTManager
from flask_restful import Api
from werkzeug.wrappers import BaseResponse

import environ
# Import my Restful api resources
from models.user import UserModel
from resources.item import ItemResource, ItemListResource
from resources.store import StoreResource, StoreListResource
from resources.todo import TodoList, Todo
from resources.token import TokenRefresh, TokenList
from resources.user import UserRegister, AllUsers, UserLogin, UserLogoutAccess, UserLogoutRefresh, \
    UserResource
from utils.blacklist_helpers import (is_token_revoked)

# Build paths inside the project like this: BASE_DIR / "directory"
BASE_DIR = Path(__file__).resolve().parent

# Create a local.env file in the settings directory
# But ideally this env file should be outside the git repo
env_file = BASE_DIR / 'local.env'
if env_file.exists():
    environ.Env.read_env(str(env_file))

env = environ.Env()

# Prevent WSGI from correcting the casing of the Location header
BaseResponse.autocorrect_location_header = False

# Find the correct template folder when running from a different location
tmpl_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'templates')
# Creating our flask app and configure it through its config dictionary
flaskApp = Flask(__name__, template_folder=tmpl_dir)

#
# if flaskApp.debug:
#     # Log everything to the logs directory at the top
#     from logging.config import dictConfig
#     LOGFILE_ROOT = BASE_DIR / 'logs'
#     LOGGING = {
#         'version': 1,
#         'formatters': {
#             'default': {
#                 'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
#             },
#             'verbose': {
#                 'format':
#                     "[%(asctime)s] %(levelname)s [%(pathname)s:%(lineno)s] %(message)s",
#                 'datefmt':
#                     "%b/%d/%Y %H:%M:%S"
#             },
#             'simple': {
#                 'format': '%(levelname)s %(message)s'
#             },
#         },
#         'handlers': {
#             'wsgi': {
#                 'class': 'logging.StreamHandler',
#                 'stream': 'ext://flask.logging.wsgi_errors_stream',
#                 'formatter': 'default'
#             },
#             'proj_log_handler': {
#                 'level': 'DEBUG',
#                 'class': 'logging.FileHandler',
#                 'filename': str(LOGFILE_ROOT / 'project.log'),
#                 'formatter': 'default'
#             },
#             'console': {
#                 'level': 'DEBUG',
#                 'class': 'logging.StreamHandler',
#                 'formatter': 'simple'
#             }
#         },
#         'root': {
#             'level': 'INFO',
#             'handlers': ['wsgi', 'proj_log_handler']
#         }
#     }
#
#     dictConfig(LOGGING)
#
# else:
#     import logging
#     from flask.logging import default_handler
#     from logging.handlers import SMTPHandler
#     # Removing the Default Handler
#     flaskApp.logger.removeHandler(default_handler)
#
#
#     mail_handler = SMTPHandler(
#         mailhost='smtp.google.com',
#         fromaddr='alexmtnezf@gmail.com',
#         toaddrs=['alexmtnezf@gmail.com'],
#         subject='Application Error')
#     mail_handler.setLevel(logging.ERROR)
#     mail_handler.setFormatter(
#         logging.Formatter(
#             '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
#
#     flaskApp.logger.addHandler(mail_handler)
#

flaskApp.config['DEBUG'] = bool(env('FLASK_DEBUG', default=True))
flaskApp.config['ENV'] = env(
    'FLASK_ENV',
    default='development')  # same as: os.environ['FLASK_ENV'] = True

if flaskApp.config['ENV'] == 'development':
    default_db_uri = env('DATABASE_URL', default='sqlite:///data.db')
else:
    default_db_uri = env(
        'DATABASE_URL', default='postgresql://test:test@localhost:5432/store')

flaskApp.config['SQLALCHEMY_DATABASE_URI'] = default_db_uri
flaskApp.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
flaskApp.config['PROPAGATE_EXCEPTIONS'] = True
flaskApp.config['SQLALCHEMY_ECHO'] = True if bool(
    env('FLASK_DEBUG', default=True)) is True else False

# SECURITY WARNING: keep the secret key used in production secret!
# Raises ImproperlyConfigured exception if SECRET_KEY not in os.environ
flaskApp.secret_key = env('SECRET_KEY')

# Creating our Restful Flask Api
flaskApp.config['BASE_API_URL'] = '/api'

# Setup the Flask-JWT-Extended extension
flaskApp.config['JWT_SECRET_KEY'] = env('SECRET_KEY')  # Change this!
# Changing the default authentication url, default /auth
flaskApp.config[
    'JWT_AUTH_URL_RULE'] = flaskApp.config['BASE_API_URL'] + '/auth'
# Where to look for a JWT when processing a request. The options are 'headers', 'cookies', or 'query_string'.
flaskApp.config['JWT_TOKEN_LOCATION'] = ['cookies', 'headers']

# Only allow JWT cookies to be sent over https. In production, this
# should likely be True
flaskApp.config['JWT_COOKIE_SECURE'] = False if env(
    'FLASK_ENV', default='development') == 'development' else True

# Set the cookie paths, so that you are only sending your access token
# cookie to the access endpoints, and only sending your refresh token
# to the refresh endpoint. Technically this is optional, but it is in
# your best interest to not send additional cookies in the request if
# they aren't needed.
flaskApp.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
flaskApp.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'

flaskApp.config['JWT_CSRF_IN_COOKIES'] = True

# Cookies with CSRF protection, setup on True in production environment
# Enable csrf double submit protection. See this for a thorough
# explanation: http://www.redotheweb.com/2015/11/09/api-security.html
flaskApp.config[
    'JWT_COOKIE_CSRF_PROTECT'] = False  # default value in Flask-JWT-Extended: true

flaskApp.config['JWT_ACCESS_CSRF_COOKIE_PATH'] = flaskApp.config[
    'JWT_ACCESS_COOKIE_PATH']
flaskApp.config['JWT_REFRESH_CSRF_COOKIE_PATH'] = flaskApp.config[
    'JWT_REFRESH_COOKIE_PATH']
# Add support of token blacklisting
flaskApp.config['JWT_BLACKLIST_ENABLED'] = True
flaskApp.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

# -----------
# Middlewares
# -----------
"""
https://github.com/kennethreitz/httpbin/issues/340
Adds a middleware to provide chunked request encoding support running under
gunicorn only.
Werkzeug required environ 'wsgi.input_terminated' to be set otherwise it
empties the input request stream.
- gunicorn seems to support input_terminated but does not add the environ,
  so we add it here.
- flask will hang and does not seem to properly terminate the request, so
  we explicitly deny chunked requests.
"""


@flaskApp.before_request
def before_request():
    if request.environ.get('HTTP_TRANSFER_ENCODING', '').lower() == 'chunked':
        server = request.environ.get('SERVER_SOFTWARE', '')
        if server.lower().startswith('gunicorn/'):
            if 'wsgi.input_terminated' in request.environ:
                flaskApp.logger.debug(
                    "environ wsgi.input_terminated already set, keeping: %s" %
                    request.environ['wsgi.input_terminated'])
            else:
                request.environ['wsgi.input_terminated'] = 1
        else:
            abort(501,
                  "Chunked requests are not supported for server %s" % server)


@flaskApp.after_request
def set_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = request.headers.get(
        'Origin', '*')
    response.headers['Access-Control-Allow-Credentials'] = 'true'

    if request.method == 'OPTIONS':
        # Both of these headers are only used for the "preflight request"
        # http://www.w3.org/TR/cors/#access-control-allow-methods-response-header
        response.headers[
            'Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
        response.headers['Access-Control-Max-Age'] = '3600'  # 1 hour cache
        if request.headers.get('Access-Control-Request-Headers') is not None:
            response.headers['Access-Control-Allow-Headers'] = request.headers[
                'Access-Control-Request-Headers']
    return response


# Initializing JWTManager for JWT token authentication and authorization
jwt = JWTManager(flaskApp)

# Using the user_claims_loader, we can specify a method that will be
# called when creating access tokens, and add these claims to the said
# token. This method is passed the identity of who the token is being
# created for, and must return data that is json serializable


# We can now get this complex object directly from the
# create_access_token method. This will allow us to access
# the properties of this object in the user_claims_loader
# function, and get the identity of this object from the
# user_identity_loader function.
@jwt.user_claims_loader
def add_claims_to_access_token(user):
    payload = {'id': user.id, 'is_admin': False, 'permissions': []}
    if user.is_admin:
        payload.update(permissions=['bar', 'foo'], is_admin=user.is_admin)

    return payload


# Create a function that will be called whenever create_access_token and create_refresh_token functions
# are used. It will take whatever object is passed into the
# create_access_token method, and lets us define what the identity
# of the access token should be.
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username


# This function is called whenever a protected endpoint is accessed,
# and must return an object based on the tokens identity.
# This is called after the token is verified, so you can use
# get_jwt_claims() in here if desired. Note that this needs to
# return None if the user could not be loaded for any reason,
# such as not being found in the underlying data store
@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    # if identity not in users_to_roles:
    #     return None

    return UserModel.find_by_username(identity)


# You can override the error returned to the user if the
# user_loader_callback returns None. If you don't override
# this, # it will return a 401 status code with the JSON:
# {"msg": "Error loading the user <identity>"}.
# You can use # get_jwt_claims() here too if desired
@jwt.user_loader_error_loader
def custom_user_loader_error(identity):
    ret = {"message": "User {} not found".format(identity)}
    return jsonify(ret), 404


# Define our callback function to check if a token has been revoked or not
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return is_token_revoked(decrypted_token)


# Whe the user submit an expired JWT token this decorator will be called
@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'description': 'Token has expired',
        'error': 'expired_token'
    }), 401


# Decorator called when the client app doesn't send a valid JWT
@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'description': 'Signature verification failed.',
        'error': 'invalid_token'
    }), 401


# Decorator called when a client app didn't send a JWT in a protected endpoint
@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'description': 'Missing JWT in cookies or headers',
        'error': 'authorization_required'
    }), 401


@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        'description':
            'Fresh token required, this token is not fresh',
        'error':
            'fresh_token_required'
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        'error':
            'token_revoked',
        'description':
            'The token sent is revoked. That means probably the user has logged out.'
    }), 401


# Swagger specification for Api Help
swagger_config = {
    "headers": [
        ('Access-Control-Allow-Origin', 'http://localhost:5000'),
        ('Access-Control-Allow-Methods', "GET, POST, PUT, DELETE, OPTIONS"),
        ('Access-Control-Allow-Credentials', "true"),
    ],
    "specs": [{
        "version": "1.0.0",
        "title": "Api v1",
        "description": 'This is the version 1 of our API',
        "endpoint": 'v1_spec',
        "route": '/v1/apispec_1.json',
        "rule_filter": lambda rule: True,  # all in
        "model_filter": lambda tag: True,  # all in
    }],
    'openapi':
        '3.0.0',
    "static_url_path":
        "/flasgger_static",
    # "static_folder": "static",  # must be set by user
    "swagger_ui":
        True,
    "specs_route":
        "/apidocs/"
}

swagger_template = {
    # "swagger": "2.0",
    # "openapi": "3.0",
    "servers": [
        {
            "url": "http://localhost:5000/",
            "description": "Development server"
        },
    ],
    "info": {
        "title":
            "Store Api",
        "description":
            "A simple HTTP Request & Response Service provided by Store API.",
        "contact": {
            "name": "Store API Support",
            "responsibleOrganization": "TechFitU",
            "responsibleDeveloper": "Alexander Martinez Fajardo",
            "url": "http://www.techfitu.com",
            "email": "alexmtnezf@techfitu.com"
        },
        "license": {
            "name": "Apache 2.0",
            "url": "http://www.apache.org/licenses/LICENSE-2.0.html"
        },
        "termsOfService":
            "/terms",
        "version":
            "1.0",
    },

    # "consumes": [
    #     "application/json",
    #     #"application/x-www-form-urlencoded"
    # ],
    # "produces": [
    #     "application/json",
    # ],
    'tags': [
        {
            'name': 'HTTP Methods',
            'description': 'Testing different HTTP verbs',
            # 'externalDocs': {'description': 'Learn more', 'url': 'https://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html'}
        },
        {
            'name': 'To-Do list',
            'description': 'Methods to interact with a memory-based To-do list'
        },
        {
            'name': 'Stores',
            'description': 'Methods for working with stores'
        },
        {
            'name': 'Items',
            'description': 'Methods for working with the store items'
        },
        {
            'name': 'Users',
            'description': 'Users methods: TESTING ONLY, REMOVE ON PRODUCTION'
        },
        {
            'name': 'Auth',
            'description': 'Auth methods'
        },
        {
            'name': 'Status codes',
            'description': 'Generates responses with given status code'
        },
        {
            'name': 'Request inspection',
            'description': 'Inspect the request data'
        },
        {
            'name': 'Response inspection',
            'description': 'Inspect the response data like caching and headers'
        },
        {
            'name': 'Response formats',
            'description': 'Returns responses in different data formats'
        },
        {
            'name': 'Dynamic data',
            'description': 'Generates random and dynamic data'
        },
        {
            'name': 'Cookies',
            'description': 'Creates, reads and deletes Cookies'
        },
        {
            'name': 'Images',
            'description': 'Returns different image formats'
        },
        {
            'name': 'Redirects',
            'description': 'Returns different redirect responses'
        },
        {
            'name': 'Anything',
            'description': 'Returns anything that is passed to request'
        },
    ]
}

flaskApp.config['SWAGGER'] = {
    'title': 'Store RESTFul API Docs',
    'uiversion': 3
}

# Our Swagger instance for deploy our APi help documentation
swagger = Swagger(flaskApp, template=swagger_template)

# Building our Restful Api
api = Api(flaskApp)

# Adding Item and Store restful resources
api.add_resource(ItemResource,
                 flaskApp.config['BASE_API_URL'] + '/item/<string:name>')
api.add_resource(StoreResource,
                 flaskApp.config['BASE_API_URL'] + '/store/<string:name>')
api.add_resource(ItemListResource, flaskApp.config['BASE_API_URL'] + '/items')
api.add_resource(StoreListResource,
                 flaskApp.config['BASE_API_URL'] + '/stores')

# Adding User restful api resources
api.add_resource(UserRegister, flaskApp.config['BASE_API_URL'] + '/register')
api.add_resource(AllUsers, flaskApp.config['BASE_API_URL'] + '/users')
api.add_resource(UserResource,
                 flaskApp.config['BASE_API_URL'] + '/user/<string:username>')
api.add_resource(UserLogin, flaskApp.config['BASE_API_URL'] + '/auth')
api.add_resource(UserLogoutAccess,
                 flaskApp.config['BASE_API_URL'] + '/logout/access')
api.add_resource(UserLogoutRefresh,
                 flaskApp.config['BASE_API_URL'] + '/logout/refresh')

api.add_resource(TokenRefresh, '/token/refresh')
api.add_resource(TokenList, flaskApp.config['BASE_API_URL'] + '/token')
# To-Do api restful resources
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<todo_id>')


# @flaskApp.errorhandler(Exception)
# def errorHandler(error):
#     """
#     This decorated function is going to handle all the JWTError exceptions generated when an authentication token
#     is mandatory in order to use our endpoints
#     :param error:
#     :return:
#     """
#     if isinstance(error, JWTError)
#     return jsonify({"message": "We could not authorize. Did you include the valid authorization header?"}), 401

from views import *

if __name__ == "__main__":
    from db import db

    db.init_app(flaskApp)

    if flaskApp.debug:
        @flaskApp.before_first_request
        def create_all_tables():
            db.create_all()

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()
    flaskApp.run(port=args.port, host=args.host)
