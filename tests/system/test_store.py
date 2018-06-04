import json

from models.item import ItemModel
from models.store import StoreModel
from models.user import UserModel
from tests.base_test import BaseTest


class StoreTest(BaseTest):
    def test_create_empty_store(self):
        with self.app_context():
            with self.client() as cl:
                resp = cl.post(StoreTest.BASE_API_URL + '/store/test')
                self.assertEqual(201, resp.status_code)
                self.assertDictEqual({'id': 1, 'name': 'test', 'items': []}, json.loads(resp.data))

    def test_create_store_duplicated(self):
        with self.app_context():
            with self.client() as cl:
                StoreModel('test').save_to_db()
                resp = cl.post(StoreTest.BASE_API_URL + '/store/test')
                self.assertEqual(400, resp.status_code)
                self.assertDictEqual({'message': "A store with name 'test' already exists."}, json.loads(resp.data))

    def test_delete_store(self):
        with self.app_context():
            with self.client() as cl:
                StoreModel('test').save_to_db()
                resp = cl.delete(StoreTest.BASE_API_URL + '/store/test')
                self.assertEqual(200, resp.status_code)
                self.assertDictEqual({'message': 'Store deleted'}, json.loads(resp.data))

    def test_delete_store_not_found(self):
        with self.app_context():
            with self.client() as cl:
                resp = cl.delete(StoreTest.BASE_API_URL + '/store/test')
                self.assertEqual(404, resp.status_code)
                self.assertDictEqual({'message': 'Store not deleted'}, json.loads(resp.data))

    def test_find_store(self):
        with self.app_context():
            with self.client() as cl:
                # Create a store
                StoreModel('test').save_to_db()
                # Register manually the user for login
                UserModel('Alex', 'alexmtnezf', '1234').save_to_db()
                # Execute login request
                auth_resp = cl.post('/auth', data=json.dumps({
                    'username': 'alexmtnezf',
                    'password': '1234'}), headers={'Content-Type': 'application/json'})

                jwt_token = json.loads(auth_resp.data).get('access_token')
                resp = cl.get(StoreTest.BASE_API_URL + '/store/test', headers={'Authorization': 'JWT ' + jwt_token})
                self.assertEqual(200, resp.status_code)
                self.assertEqual({'id': 1, 'name': 'test', 'items': []}, json.loads(resp.data))

    def test_find_store_with_items(self):
        with self.app_context():
            with self.client() as cl:
                # Create a store and one item for the store
                StoreModel('test').save_to_db()
                ItemModel('Item1', 19.99, 1).save_to_db()
                # Register manually the user for login
                UserModel('Alex', 'alexmtnezf', '1234').save_to_db()
                # Execute login request
                auth_resp = cl.post('/auth', data=json.dumps({
                    'username': 'alexmtnezf',
                    'password': '1234'}), headers={'Content-Type': 'application/json'})

                jwt_token = json.loads(auth_resp.data).get('access_token')
                resp = cl.get(StoreTest.BASE_API_URL + '/store/test', headers={'Authorization': 'JWT ' + jwt_token})
                self.assertEqual(200, resp.status_code)
                self.assertEqual({
                    'id': 1,
                    'name': 'test',
                    'items': [{
                        'name': 'Item1',
                        'price': 19.99,
                        'store_id': 1
                    }]}, json.loads(resp.data))

    def test_find_store_not_found(self):
        with self.app_context():
            with self.client() as cl:
                # Register manually the user for login
                UserModel('Alex', 'alexmtnezf', '1234').save_to_db()
                # Execute login request
                auth_resp = cl.post('/auth', data=json.dumps({
                    'username': 'alexmtnezf',
                    'password': '1234'}), headers={'Content-Type': 'application/json'})

                jwt_token = json.loads(auth_resp.data).get('access_token')
                resp = cl.get(StoreTest.BASE_API_URL + '/store/test', headers={'Authorization': 'JWT ' + jwt_token})
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
                resp = cl.get(StoreTest.BASE_API_URL + '/stores')
                self.assertEqual(200, resp.status_code)
                self.assertDictEqual({
                    'stores': [
                        {'id': 1, 'name': 'test', 'items': []}
                    ]}, json.loads(resp.data))

    def test_store_list_with_items(self):
        with self.app_context():
            with self.client() as cl:
                StoreModel('test').save_to_db()
                ItemModel('Item1', 19.99, 1).save_to_db()

                resp = cl.get(StoreTest.BASE_API_URL + '/stores')
                self.assertEqual(200, resp.status_code)
                self.assertDictEqual({
                    'stores': [{
                        'id': 1,
                        'name': 'test',
                        'items': [
                            {'name': 'Item1', 'price': 19.99, 'store_id': 1}
                        ]
                    }]
                }, json.loads(resp.data))
