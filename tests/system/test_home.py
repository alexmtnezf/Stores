import json

from tests.base_test import BaseTest


class TestHome(BaseTest):
    def test_home(self):
        with self.client() as c:
            response = c.get('/')
            self.assertEqual(200, response.status_code)
            self.assertDictEqual({"message": "hello world"},
                                 json.loads(response.get_data()),
                                 "The response {} is not the same as expected {}".format(
                                     json.loads(response.get_data()),
                                     {"message": "hello world"}))
