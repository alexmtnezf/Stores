import json

from models.item import ItemModel
from models.store import StoreModel
from models.user import UserModel
from tests.base_test import BaseTest


class ItemTest(BaseTest):
    USER_ID = None

    def setUp(self):
        super(ItemTest, self).setUp()
        with self.app_context():
            with self.client() as client:
                # Register manually the user for login
                UserModel(
                    'Alex', 'alexmtnezf', '1234', is_admin=True).save_to_db()
                # Execute login request
                auth_resp = client.post(
                    ItemTest.BASE_API_URL + '/auth',
                    data=json.dumps({
                        'username': 'alexmtnezf',
                        'password': '1234'
                    }),
                    headers={'Content-Type': 'application/json'})

                data = auth_resp.data.decode(
                    'utf-8'
                )  # Decode binary buffer before parsing it to JSON objects
                data = json.loads(data)
                jwt_token = data.get('access_token')
                ItemTest.USER_ID = data.get('user_id')

                self.headers = {'Authorization': 'Bearer {}'.format(jwt_token)}

    def test_create_item(self):
        with self.app_context():
            with self.client() as cl:
                StoreModel('Store1').save_to_db()
                resp = cl.post(
                    ItemTest.BASE_API_URL + '/item/test',
                    data={
                        'price': 40.2,
                        'store_id': 1,
                        'user_id': ItemTest.USER_ID
                    },
                    headers=self.headers)
                self.assertEqual(201, resp.status_code)
                self.assertDictEqual({
                    'name': 'test',
                    'price': 40.2,
                    'store_id': 1
                }, json.loads(resp.data.decode('utf-8')))

    def test_create_duplicate_item(self):
        with self.app_context():
            with self.client() as cl:
                StoreModel('Store1').save_to_db()
                ItemModel(name='test', price=40.2, store_id=1).save_to_db()
                resp = cl.post(
                    ItemTest.BASE_API_URL + '/item/test',
                    data={
                        'price': 40.2,
                        'store_id': 1
                    },
                    headers=self.headers)
                self.assertEqual(400, resp.status_code)
                self.assertDictEqual(
                    {
                        'message': "An item with name 'test' already exists."
                    }, json.loads(resp.data.decode('utf-8')))

    def test_delete_item(self):
        with self.app_context():
            with self.client() as cl:
                StoreModel('Store1').save_to_db()
                ItemModel(name='test', price=40.2, store_id=1).save_to_db()
                resp = cl.delete(
                    ItemTest.BASE_API_URL + '/item/test', headers=self.headers)
                self.assertEqual(200, resp.status_code)

    def test_delete_item_not_found(self):
        with self.app_context():
            with self.client() as cl:
                resp = cl.delete(
                    ItemTest.BASE_API_URL + '/item/test', headers=self.headers)
                self.assertEqual(200, resp.status_code)
                self.assertDictEqual({
                    'message': 'Item deleted'
                }, json.loads(resp.data.decode('utf-8')))

    def test_get_item(self):
        with self.app_context():
            with self.client() as cl:
                # Create a store and one item for the store
                StoreModel('test').save_to_db()
                ItemModel('Item1', 19.99, 1).save_to_db()
                resp = cl.get(
                    ItemTest.BASE_API_URL + '/item/Item1',
                    headers=self.headers)
                self.assertEqual(200, resp.status_code)
                self.assertDictEqual({
                    'name': 'Item1',
                    'price': 19.99,
                    'store_id': 1
                }, json.loads(resp.data.decode('utf-8')))

    def test_get_item_no_authenticated_user(self):
        with self.app_context():
            with self.client() as cl:
                # Not-Authorized code: 401
                resp = cl.get(ItemTest.BASE_API_URL + '/item/test')
                self.assertEqual(401, resp.status_code)

    def test_get_item_not_found(self):
        with self.app_context():
            with self.client() as cl:
                resp = cl.get(
                    ItemTest.BASE_API_URL + '/item/Item1',
                    headers=self.headers)
                self.assertEqual(404, resp.status_code)
                self.assertDictEqual({
                    'message': 'Item not found'
                }, json.loads(resp.data.decode('utf-8')))

    def test_put_item(self):
        with self.app_context():
            with self.client() as cl:
                # Create a store
                StoreModel('test').save_to_db()

                resp = cl.put(
                    ItemTest.BASE_API_URL + '/item/test',
                    data={
                        'price': 40.2,
                        'store_id': 1,
                        'user_id': ItemTest.USER_ID
                    },
                    headers=self.headers)
                self.assertEqual(201, resp.status_code)
                self.assertDictEqual({
                    'name': 'test',
                    'price': 40.2,
                    'store_id': 1
                }, json.loads(resp.data.decode('utf-8')))

    def test_put_update_item(self):
        with self.app_context():
            with self.client() as cl:
                # Create a store and item for the store
                StoreModel('test').save_to_db()
                ItemModel('test', 40.2, 1).save_to_db()

                self.assertEqual(40.2, ItemModel.find_by_name('test').price)

                resp = cl.put(
                    ItemTest.BASE_API_URL + '/item/test',
                    data={
                        'price': 30.2,
                        'store_id': 1,
                        'user_id': ItemTest.USER_ID
                    },
                    headers=self.headers)
                self.assertEqual(200, resp.status_code)
                self.assertEqual(30.2, ItemModel.find_by_name('test').price)
                self.assertDictEqual({
                    'name': 'test',
                    'price': 30.2,
                    'store_id': 1
                }, json.loads(resp.data.decode('utf-8')))

    def test_item_list_empty(self):
        with self.app_context():
            with self.client() as cl:
                resp = cl.get(
                    ItemTest.BASE_API_URL + '/items', headers=self.headers)
                self.assertEqual(200, resp.status_code)
                self.assertDictEqual({
                    'items': []
                }, json.loads(resp.data.decode('utf-8')))

    def test_item_list(self):
        with self.app_context():
            with self.client() as cl:
                # Create a store and item for the store
                StoreModel('test').save_to_db()
                ItemModel('test', 40.2, 1).save_to_db()
                resp = cl.get(
                    ItemTest.BASE_API_URL + '/items', headers=self.headers)
                self.assertEqual(200, resp.status_code)
                self.assertDictEqual({
                    'items': [{
                        'name': 'test',
                        'price': 40.2,
                        'store_id': 1
                    }]
                }, json.loads(resp.data.decode('utf-8')))
