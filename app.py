import os

from flask import Flask, jsonify
from flask_jwt import JWT, JWTError
from flask_restful import Api

# Import my Restful api resources
from resources.item import ItemResource, ItemListResource
from resources.store import StoreResource, StoreListResource
from resources.user import UserRegister
from security import authenticate, identity

# Creating our flask app and configure it through its config dictionary
flaskApp = Flask(__name__)
flaskApp.config['DEBUG'] = True  # same as: os.environ['FLASK_DEBUG'] = 'True'
flaskApp.config['ENV'] = 'development'  # same as: os.environ['FLASK_ENV'] = 'development'

# For sqlite, sqlite:///data.db
# For postgresql: 'postgresql://test:test@localhost:5432/store'
flaskApp.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
flaskApp.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# flaskApp.config['PROPAGATE_EXCEPTIONS'] = True
flaskApp.secret_key = 'jose123'

# Creating our Restful Flask Api
flaskApp.config['BASE_API_URL'] = '/api'
api = Api(flaskApp)

# The jwt object takes or flask app, the authentication and identity handlers and link them all.
jwt = JWT(flaskApp, authenticate, identity)  # Calling /auth we'll use Flask-JWT to verify the token is correct.

# Adding restful resources
api.add_resource(ItemResource, flaskApp.config['BASE_API_URL'] + '/item/<string:name>')
api.add_resource(StoreResource, flaskApp.config['BASE_API_URL'] + '/store/<string:name>')
api.add_resource(ItemListResource, flaskApp.config['BASE_API_URL'] + '/items')
api.add_resource(StoreListResource, flaskApp.config['BASE_API_URL'] + '/stores')

api.add_resource(UserRegister, flaskApp.config['BASE_API_URL'] + '/register')


@flaskApp.route('/')
def home():
    return jsonify({'message': 'hello world'})

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

    if flaskApp.config['DEBUG'] is True:
        @flaskApp.before_first_request
        def create_all_tables():
            db.create_all()


    flaskApp.run(port=5000)
