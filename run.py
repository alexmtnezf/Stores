# -*- coding: utf-8 -*-
from app import flaskApp as application
from db import db


# Flask app configuration
db.init_app(application)

@application.before_first_request
def create_tables():
    db.create_all()

