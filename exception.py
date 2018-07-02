# -*- coding: utf-8 -*-


class TokenNotFound(Exception):
    """
    Indicates that a token could not be found in the database
    """
    pass


class ItemNotFoundError(Exception):
    """
    Indicates that an item could not be found in the database
    """
    pass
