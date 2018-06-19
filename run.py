from app import flaskApp
from db import db

db.init_app(flaskApp)

@flaskApp.before_first_request
def create_tables():
    db.create_all()
