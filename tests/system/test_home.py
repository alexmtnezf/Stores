# -*- coding: utf-8 -*-
import json

from tests.base_test import BaseTest


class TestHome(BaseTest):
    def test_home(self):
        with self.client() as c:
            response = c.get('/home')
            self.assertEqual(200, response.status_code)
            self.assertDictEqual(
                {
                    "message": "Hello, World!"
                }, json.loads(response.get_data().decode("utf-8")),
                "The response {} is not the same as expected {}".format(
                    json.loads(response.get_data().decode("utf-8")),
                    {"message": "Hello, World!"}))
