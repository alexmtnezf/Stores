"""
StoreModel class
"""

from db import db
from models.base_model import BaseModel
from models.item import ItemModel


class StoreModel(db.Model, BaseModel):
    __tablename__ = 'stores'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    items = db.relationship('ItemModel', lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def json(self):
        return {'id': self.id, 'name': self.name, 'items': [item.json() for item in self.items.all()]}

    def create_item(self, name, price):
        ItemModel(name, price, self.id).save_to_db()
