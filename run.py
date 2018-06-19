import multiprocessing

from app import flaskApp as application
from db import db

import os
ON_HEROKU = os.environ.get('ON_HEROKU')
if ON_HEROKU:
    # get the heroku port
    port = int(os.environ.get("PORT", 17995))  # as per OP comments default is 17995
else:
    port = 3000

# Gunicorn configs
bind = "0.0.0.0:{}".format(port)
workers = multiprocessing.cpu_count() * 2 + 1

# End

# Flask app configuration
db.init_app(application)

@application.before_first_request
def create_tables():
    db.create_all()
