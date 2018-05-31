"""
BaseTest

This class should be the parent class to each non-unit test class.
It allows for instantiation of the database dynamically,
and makes sure that it is a new, blank database each time.
"""

from unittest import TestCase

from app import flaskApp
from db import db


class BaseTest(TestCase):
    def setUp(self):
        # Set my flask app to test mode
        flaskApp.testing = True
        # Make sure your database is created
        # For PostgreSQL the connection string: postgresql://user:password@localhost:port/database
        flaskApp.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"
        with flaskApp.app_context():
            db.init_app(flaskApp)
            db.create_all()

        # Get a test client for system tests and an app context for integration tests.
        self.app_context = flaskApp.app_context
        self.client = flaskApp.test_client

    def tearDown(self):
        # Database is blank
        with flaskApp.app_context():
            db.session.remove()
            db.drop_all()

        # delete every object created in setUp
        del self.client
        del self.app_context
