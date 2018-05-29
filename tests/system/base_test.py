from unittest import TestCase

from app import flaskApp


class TestBase(TestCase):
    def setUp(self):
        flaskApp.testing = True
        self.client = flaskApp.test_client

    def tearDown(self):
        del self.client
