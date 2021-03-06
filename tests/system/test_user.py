# -*- coding: utf-8 -*-
import json

from models.user import UserModel
from tests.base_test import BaseTest


class UserTest(BaseTest):
    def test_register_user(self):
        with self.app_context():
            with self.client() as c:
                # Registering the user, data is been sent as a form data
                response = c.post(
                    UserTest.BASE_API_URL + '/register',
                    data={
                        'name': 'nueva',
                        'username': 'pepito',
                        'password': 'abcd'
                    })

                self.assertEqual(201, response.status_code)
                self.assertIsNotNone(UserModel.find_by_username('pepito'))
                self.assertDictEqual({
                    "message": "User created successfully."
                }, json.loads(response.get_data().decode('utf-8')))

    def test_register_duplicate_user(self):
        with self.app_context():
            with self.client() as c:
                UserModel(
                    'Alex', 'alexmtnezf', '1234', is_admin=True).save_to_db()

                # Registering the user, data is been sent as a form data
                response = c.post(
                    UserTest.BASE_API_URL + '/register',
                    data={
                        'name': 'Alex',
                        'username': 'alexmtnezf',
                        'password': '1234'
                    })
                self.assertEqual(400, response.status_code)
                self.assertDictEqual(
                    {
                        "message": "A user with that username already exists"
                    }, json.loads(response.data.decode('utf-8')))

    def test_register_and_login(self):
        with self.app_context():
            with self.client() as c:
                # Registering the user, data is been sent as a form data
                c.post(
                    UserTest.BASE_API_URL + '/register',
                    data={
                        'name': 'Alex',
                        'username': 'alexmtnezf',
                        'password': '1234'
                    })

                # Login the user, data is been sent as a json data payload
                auth_response = c.post(
                    UserTest.BASE_API_URL + '/auth',
                    data=json.dumps({
                        'username': 'alexmtnezf',
                        'password': '1234'
                    }),
                    headers={'Content-Type': 'application/json'})

                # The response from Flask-JWT authentication is a string that is decoded and gives us a dictionary
                # with a key that has the access token, that needs to be sent in the following requests
                self.assertIn('access_token',
                              json.loads(auth_response.data.decode('utf-8'))
                              .keys())  # ['access_token']

    def test_user_can_login(self):
        pass

    def test_user_cannot_login(self):
        with self.app_context():
            with self.client() as c:
                UserModel(
                    'Alex', 'alexmtnezf', '1234', is_admin=True).save_to_db()

                # Registering the user, data is been sent as a form data
                response = c.post(
                    UserTest.BASE_API_URL + '/auth',
                    data=json.dumps({
                        'username': 'alexmtnezf',
                        'password': 'dasdads'
                    }),
                    headers={'Content-Type': 'application/json'})
                self.assertEqual(401, response.status_code)
                self.assertDictEqual({
                    'message': 'Wrong credentials'
                }, json.loads(response.data.decode('utf-8')))
