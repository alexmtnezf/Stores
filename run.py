# -*- coding: utf-8 -*-
from multiprocessing import cpu_count

from app import flaskApp as application
from db import db

##### Gunicorn configs#####
# Server Socket
#bind = "0.0.0.0:{}".format(port)


# Worker Processes
workers = cpu_count() * 2 + 1  # Valor recomendado por la doc oficial: http://docs.gunicorn.org/en/stable/design.html#how-many-workers

###### End Gunicorn settings#####

# Flask app configuration
db.init_app(application)


@application.before_first_request
def create_tables():
    db.create_all()

