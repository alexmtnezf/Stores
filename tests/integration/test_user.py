"""
StoreTest
Class tested: StoreModel

Only test methods that depends on databases or work with other classes and methods of your app
"""

from models.user import UserModel
from tests.base_test import BaseTest


class UserTest(BaseTest):
    def test_crud(self):
        """
        Tests the delete_from_db and save_to_db methods of UserModel
        :return: None
        """
        with self.app_context():
            user = UserModel('Alex', 'alexmtnezf', '12345', is_admin=True)
            self.assertIsNone(UserModel.find_by_name('Alex'))
            self.assertIsNone(UserModel.find_by_username('alexmtnezf'))
            self.assertIsNone(UserModel.find_by_id(1))

            user.save_to_db()
            self.assertIsNotNone(UserModel.find_by_name('Alex'))
            self.assertIsNotNone(UserModel.find_by_username('alexmtnezf'))
            self.assertIsNotNone(UserModel.find_by_id(1))

            user.delete_from_db()
            self.assertIsNone(UserModel.find_by_name('Alex'))
            self.assertIsNone(UserModel.find_by_username('alexmtnezf'))
            self.assertIsNone(UserModel.find_by_id(1))
