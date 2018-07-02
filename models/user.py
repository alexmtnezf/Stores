# -*- coding: utf-8 -*-

from passlib.hash import pbkdf2_sha256 as sha256

from db import db
from .base_model import BaseModel


class UserModel(db.Model, BaseModel):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    username = db.Column(db.String(80))
    password = db.Column(
        db.String(256)
    )  # OJO: no podemos dejar de ponerle maxlength en SQLite a los campos de tabla
    is_admin = db.Column(db.Boolean())

    def __init__(self, name, username, password, is_admin):
        self.username = username
        self.name = name
        self.password = UserModel.generate_hash(
            password)  # Encrypt password before save it
        self.is_admin = is_admin

    def __str__(self):
        return "User(id='%s')" % self.id

    def json(self):
        return {'id': self.id, 'username': self.username, 'name': self.name}

    # Class methods
    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Something went wrong'}

    # Static methods
    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)
