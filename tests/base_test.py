# -*- coding: utf-8 -*-
"""
BaseTest

This class should be the parent class to each non-unit test class.
It allows for instantiation of the database dynamically,
and makes sure that it is a new, blank database each time.
"""

from unittest import TestCase

from app import flaskApp, default_db_uri
from db import db


class BaseTest(TestCase):
    # Class variables
    SQLALCHEMY_DATABASE_URI = default_db_uri  #
    BASE_API_URL = flaskApp.config['BASE_API_URL']

    @classmethod
    def setUpClass(cls):
        """
        It runs once and before all the test methods in this class and derived class
        :return: None
        """
        # Set my flask app to test mode
        # flaskApp.testing = True

        # For PostgreSQL in production: postgresql://user:password@localhost:port/database
        # Configure once the database uri for all tests
        flaskApp.config[
            'SQLALCHEMY_DATABASE_URI'] = BaseTest.SQLALCHEMY_DATABASE_URI
        flaskApp.config['DEBUG'] = False
        flaskApp.config['SQLALCHEMY_ECHO'] = False
        flaskApp.config['PROPAGATE_EXCEPTIONS'] = True

        # Initialize our database once for every test suite (every test file that contains a BaseTest derived class)
        with flaskApp.app_context():
            db.init_app(flaskApp)

    def setUp(self):
        """
        It runs once for every test method in this class and derived class
        :return: None
        """
        # Make sure your database is created
        with flaskApp.app_context():

            db.create_all()

        # Get a test client and app context for integration and system tests.
        self.app_context = flaskApp.app_context
        self.client = flaskApp.test_client

    def tearDown(self):
        # Database is blank
        with flaskApp.app_context():
            db.session.remove()
            db.drop_all()
