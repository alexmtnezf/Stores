import os
from flask import Flask
from flask import jsonify
#from flask_restful import Api

# Import my Restful api resources

#from resources.item import ItemResource, ItemListResource
#from resources.store import StoreResource, StoreListResource


flaskApp = Flask(__name__)
flaskApp.config['DEBUG'] = True
flaskApp.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','sqlite:///data.db')
flaskApp.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Creating our Restful Api
#api = Api(flaskApp)

#Adding restful resources
#api.add_resource(ItemResource, '/item/<string:name>')
#api.add_resource(StoreResource, '/item/<string:name>')
#api.add_resource(ItemListResource, '/items')
#api.add_resource(StoreListResource, '/stores')


@flaskApp.route("/")
def home():
    return jsonify({"message": "hello world"})


if __name__ == "__main__":
    from db import db
    db.init_app(flaskApp)

    if flaskApp.config['DEBUG'] is True:
        @flaskApp.before_first_request
        def create_all_tables():
            db.create_all()


    flaskApp.run(port=5000)
