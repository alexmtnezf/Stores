"""
ItemTest
Class tested: StoreModel

Only test methods that depends on databases or work with other classes and methods of your app
"""

from models.item import ItemModel
from models.store import StoreModel
from tests.base_test import BaseTest


class ItemTest(BaseTest):
    def test_crud(self):
        """
        Tests the delete_from_db and save_to_db methods of StoreModel
        :return: None
        """
        with self.app_context():
            StoreModel(name='Store 1').save_to_db()
            # Testing ForeignKey constraint in this integration test
            item = ItemModel('test', 19.99, 1)

            self.assertIsNone(ItemModel.find_by_name('test'))
            item.save_to_db()
            self.assertIsNotNone(ItemModel.find_by_name('test'))
            item.name = 'Item2'
            item.save_to_db()
            self.assertIsNotNone(ItemModel.find_by_name('Item2'))
            item.delete_from_db()
            self.assertIsNone(ItemModel.find_by_name('test'))

    def test_store_relationship(self):
        """
        Test if the relationship is correct, when a store and item are already related in the database
        :return:
        """
        with self.app_context():
            StoreModel('store').save_to_db()
            # Testing ForeignKey constraint in this integration test
            item = ItemModel('item1', 19.99, 1)
            item.save_to_db()
            self.assertEqual('store', item.store.name)
            # Testing that ForeignKey constraint raises an IntegrityError exception when try to relation an item
            # with a non-existent Store.
            with self.assertRaises(Exception):
                ItemModel('item2', 99.32, 2).save_to_db()
