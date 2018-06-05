from db import db


class BaseModel(object):
    def __repr__(self):
        return str(self.__dict__)

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by(cls, **kwargs):
        return cls.query.filter_by(**kwargs)

    def json(self):
        raise NotImplementedError()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
        return self
