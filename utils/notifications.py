# -*- coding: utf-8 -*-

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from twilio.rest import Client
from environ import Env


class NotificationDispatcher(object):
    @classmethod
    def send_sms(cls, from_name, to_name, to_phone, text):
        env = Env()
        client = Client(
            env('ACCOUNT_SID', default='ACd2c4870ba6657809de3fbd55b14647a1'),
            env('AUTH_TOKEN', default='9eaf6fff15d756ab219b9dcc43404129'))

        message = client.messages.create(
            body='\nFrom: {}\nTo: {}\n{}'.format(from_name, to_name, text),
            from_='+13058594740',
            to=to_phone)

        return message.sid


if __name__ == "__main__":
    NotificationDispatcher.send_sms('Alex', 'Niobis', '+12106105564',
                                    'Felicidades')
