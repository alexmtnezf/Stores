import json

from models.item import ItemModel
from models.store import StoreModel
from models.user import UserModel
from tests.base_test import BaseTest


class StoreTest(BaseTest):
    USER_ID = None

    def setUp(self):
        super(StoreTest, self).setUp()
        with self.app_context():
            with self.client() as client:
                # Register manually the user for login
                UserModel('Alex', 'alexmtnezf', '1234', is_admin=True).save_to_db()
                # Execute login request
                auth_resp = client.post(StoreTest.BASE_API_URL + '/auth', data=json.dumps({
                    'username': 'alexmtnezf',
                    'password': '1234'}), headers={'Content-Type': 'application/json'})

                data = auth_resp.data.decode('utf-8')  # Decode binary buffer before parsing it to JSON objects
                data = json.loads(data)
                jwt_token = data.get('access_token')
                StoreTest.USER_ID = data.get('user_id')

                self.headers = {'Authorization': 'Bearer {}'.format(jwt_token)}

    def test_create_empty_store(self):
        with self.app_context():
            with self.client() as cl:
                resp = cl.post(StoreTest.BASE_API_URL + '/store/test', headers=self.headers)
                self.assertEqual(201, resp.status_code)
                self.assertDictEqual({'id': 1, 'name': 'test', 'items': []}, json.loads(resp.data.decode('utf-8')))

    def test_create_store_duplicated(self):
        with self.app_context():
            with self.client() as cl:
                StoreModel('test').save_to_db()
                resp = cl.post(StoreTest.BASE_API_URL + '/store/test', headers=self.headers)
                self.assertEqual(400, resp.status_code)
                self.assertDictEqual({'message': "A store with name 'test' already exists."},
                                     json.loads(resp.data.decode('utf-8')))

    def test_delete_store(self):
        with self.app_context():
            with self.client() as cl:
                StoreModel('test').save_to_db()
                resp = cl.delete(StoreTest.BASE_API_URL + '/store/test', headers=self.headers)
                self.assertEqual(200, resp.status_code)
                self.assertDictEqual({'message': 'Store deleted'}, json.loads(resp.data.decode('utf-8')))

    def test_delete_store_not_found(self):
        with self.app_context():
            with self.client() as cl:
                resp = cl.delete(StoreTest.BASE_API_URL + '/store/test', headers=self.headers)
                # The DELETE method es Idempotent, if the store not exists, it will return 200 status code anyways
                self.assertEqual(200, resp.status_code)
                # self.assertDictEqual({'message': "Store test doesn't exist"}, json.loads(resp.data.decode('utf-8')))

    def test_find_store(self):
        with self.app_context():
            with self.client() as cl:
                # Create a store
                StoreModel('test').save_to_db()
                # Register manually the user for login

                resp = cl.get(StoreTest.BASE_API_URL + '/store/test', headers=self.headers)
                self.assertEqual(200, resp.status_code)
                self.assertEqual({'id': 1, 'name': 'test', 'items': []}, json.loads(resp.data.decode('utf-8')))

    def test_find_store_with_items(self):
        with self.app_context():
            with self.client() as cl:
                # Create a store and one item for the store
                StoreModel('test').save_to_db()
                ItemModel('Item1', 19.99, 1).save_to_db()

                resp = cl.get(StoreTest.BASE_API_URL + '/store/test', headers=self.headers)
                self.assertEqual(200, resp.status_code)
                self.assertEqual({
                    'id': 1,
                    'name': 'test',
                    'items': [{
                        'name': 'Item1',
                        'price': 19.99,
                        'store_id': 1
                    }]}, json.loads(resp.data.decode('utf-8')))

    def test_find_store_not_found(self):
        with self.app_context():
            with self.client() as cl:
                resp = cl.get(StoreTest.BASE_API_URL + '/store/test', headers=self.headers)
                self.assertEqual(404, resp.status_code)

    def test_store_without_login(self):
        with self.app_context():
            with self.client() as cl:
                resp = cl.get(StoreTest.BASE_API_URL + '/store/test')
                # Not-Authorized code: 401
                self.assertEqual(401, resp.status_code)

    def test_store_list(self):
        with self.app_context():
            with self.client() as cl:
                StoreModel('test').save_to_db()
                resp = cl.get(StoreTest.BASE_API_URL + '/stores', headers=self.headers)
                self.assertEqual(200, resp.status_code)
                self.assertDictEqual({
                    'stores': [
                        {'id': 1, 'name': 'test', 'items': []}
                    ]}, json.loads(resp.data.decode('utf-8')))

    def test_store_list_with_items(self):
        with self.app_context():
            with self.client() as cl:
                StoreModel('test').save_to_db()
                ItemModel('Item1', 19.99, 1).save_to_db()

                resp = cl.get(StoreTest.BASE_API_URL + '/stores', headers=self.headers)
                self.assertEqual(200, resp.status_code)
                self.assertDictEqual({
                    'stores': [{
                        'id': 1,
                        'name': 'test',
                        'items': [
                            {'name': 'Item1', 'price': 19.99, 'store_id': 1}
                        ]
                    }]
                }, json.loads(resp.data.decode('utf-8')))
