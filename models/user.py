from db import db
from .base_model import BaseModel


class UserModel(db.Model, BaseModel):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    username = db.Column(db.String(80))
    password = db.Column(db.String(80))  # OJO: no podemos dejar de ponerle maxlength en SQLite a los campos de tabla

    def __init__(self, name, username, password):
        self.username = username
        self.name = name
        self.password = password

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()
