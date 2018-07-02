# -*- coding: utf-8 -*-
from flask import request


def secure_cookie():
    """Return true if cookie should have secure attribute"""
    return request.environ.get('wsgi.url_scheme', None) == 'https'
