# -*- coding: utf-8 -*-
import multiprocessing

from app import flaskApp as application
from db import db

# Gunicorn configs
#bind = "0.0.0.0:{}".format(port)
workers = multiprocessing.cpu_count() * 2 + 1

# End Gunicorn settings

# Flask app configuration
db.init_app(application)


@application.before_first_request
def create_tables():
    db.create_all()

