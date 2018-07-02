# -*- coding: utf-8 -*-
"""
SMSNotificationTest
Class tested: NotificationDispatcher

Only test methods that depends on twilio or work with other classes and methods of your app
"""
from tests.base_test import BaseTest
from utils.notifications import NotificationDispatcher


class SMSNotificationTest(BaseTest):
    def test_send_sms(self):
        msg_id = NotificationDispatcher.send_sms('Alex', 'Niobis', '+12106105564',
                                                 'Felicidades')

        self.assertTrue(msg_id)
