"""
StoreTest

Only test methods that don't depend on databases or other classes of your app
"""

from models.store import StoreModel
from tests.unit.unit_base_test import UnitBaseTest


class StoreTest(UnitBaseTest):

    def test_create_store(self):
        """
        Test the __init__ method of StoreModel
        :return:
        """
        store = StoreModel(name='store1')
        self.assertEqual('store1', store.name)
