# -*- coding: utf-8 -*-
from flask import current_app
from sqlalchemy.exc import IntegrityError

from db import db


class BaseModel(object):
    def __repr__(self):
        return str(self.__dict__)

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by(cls, **kwargs):
        return cls.query.filter_by(**kwargs)

    def json(self):
        raise NotImplementedError()

    def save_to_db(self):
        try:
            db.session.add(self)
            db.session.commit()
        except IntegrityError as ex:
            current_app.logger.error('\nDatabase error: {0} \n'.format(ex))
            raise Exception(
                'The related object to the one you are inserting is doesn\'t exist'
            )
        return self

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
        return self
