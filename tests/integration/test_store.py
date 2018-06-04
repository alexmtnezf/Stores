"""
StoreTest
Class tested: StoreModel

Only test methods that depends on databases or work with other classes and methods of your app
"""

from models.item import ItemModel
from models.store import StoreModel
from tests.base_test import BaseTest


class StoreTest(BaseTest):

    def test_create_store_empty(self):
        """
        Tests if the items of the store are empty, when the store is just instantiated
        :return: None
        """
        store = StoreModel('store1')
        self.assertListEqual([], store.items.all())
        self.assertEqual(0, len(store.items.all()))

    def test_crud(self):
        """
        Tests the delete_from_db and save_to_db methods of StoreModel
        :return: None
        """
        with self.app_context():
            store = StoreModel('test')
            self.assertIsNone(StoreModel.find_by_name('test'))
            store.save_to_db()
            self.assertIsNotNone(StoreModel.find_by_name('test'))
            store.delete_from_db()
            self.assertIsNone(StoreModel.find_by_name('test'))

    def test_items_relationship(self):
        """
        Test if the relationship is correct when a store and item are already related in the database
        :return:
        """
        with self.app_context():
            store = StoreModel(name='test')
            store.save_to_db()
            item = ItemModel('item1', 19.99, 1)
            item.save_to_db()

            self.assertEqual(1, store.items.count())
            self.assertEqual(item.name, store.items.first().name)

    def test_store_json_with_items(self):
        """
        Tests if json method returns a dic() instance with items list added on it
        :return: None
        """
        with self.app_context():
            store = StoreModel(name='test')
            store.save_to_db()
            ItemModel('Item1', 19.99, 1).save_to_db()
            expected = {
                'id': 1,
                'name': 'test',
                'items': [{
                    "name": "Item1",
                    "price": 19.99,
                    "store_id": 1
                }]
            }

            self.assertDictEqual(expected, store.json())

    def test_store_json_no_items(self):
        """
        Tests if json method returns a dic() instance of the store,
        with items list empty, and added on it
        :return: None
        """
        with self.app_context():
            store = StoreModel(name='test')
            store.save_to_db()
            expected = {
                'id': 1,
                'name': 'test',
                'items': []
            }

            self.assertDictEqual(expected, store.json())

    def test_create_item_in_store(self):
        with self.app_context():
            store = StoreModel(name='test')
            store.save_to_db()

            store.create_item('Item1', 20.99)
            self.assertEqual(1, len(store.items.all()))
            # Get the Item1 created
            item = store.items.first()
            self.assertEqual('Item1', item.name)
            self.assertEqual(20.99, item.price)
            self.assertEqual(1, item.store_id)

            # Create the second item
            store.create_item('Item2', 20.99)
            self.assertEqual(2, len(store.items.all()))

            # Get the Item2 created
            item2 = store.items[1]
            self.assertEqual('Item2', item2.name)
            self.assertEqual(20.99, item2.price)
            self.assertEqual(1, item2.store_id)
