from app import flaskApp
from db import db

db.init_app(flaskApp)

if flaskApp.config['DEBUG']:
    @flaskApp.before_first_request
    def create_tables():
        db.create_all()

flaskApp.run(port=5000)
