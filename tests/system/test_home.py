import json

from .base_test import TestBase


class TestHome(TestBase):
    def test_home(self):
        with self.client() as c:
            response = c.get('/')
            self.assertEqual(200, response.status_code)
            self.assertDictEqual({"message": "hello world"},
                                 json.loads(response.get_data()),
                                 "The response {} is not the same as expected {}".format(
                                     json.loads(response.get_data()),
                                     {"message": "hello world"}))
