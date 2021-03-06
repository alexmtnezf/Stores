# -*- coding: utf-8 -*-
"""
models/item.py

Module that contains the model definition for items in a SQLAlchemy database.
"""
from db import db
from .base_model import BaseModel


class ItemModel(db.Model, BaseModel):
    """
    ItemModel class
    """
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    price = db.Column(db.Float(precision=2))

    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    store = db.relationship('StoreModel')

    def __init__(self, name, price, store_id, **kwargs):
        self.name = name
        self.price = price
        self.store_id = store_id

    def json(self):
        return {
            'name': self.name,
            'price': self.price,
            'store_id': self.store_id
        }
