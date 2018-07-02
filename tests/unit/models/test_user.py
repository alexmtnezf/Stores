# -*- coding: utf-8 -*-
"""
UserTest

Only test methods that don't depend on databases or other classes of your app
"""

from models.user import UserModel
from tests.unit.unit_base_test import UnitBaseTest


class UserTest(UnitBaseTest):
    def test_create_user(self):
        """
        Test the __init__ method of UserModel
        :return:
        """
        user = UserModel('Alexander', 'alexmtnezf', '12345', is_admin=True)
        self.assertEqual('alexmtnezf', user.username)
        assert UserModel.verify_hash('12345', user.password)
        self.assertEqual('Alexander', user.name)
        self.assertTrue(user.is_admin)
