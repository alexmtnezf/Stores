# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy.orm.exc import NoResultFound

from db import db
from .base_model import BaseModel


class TokenModel(db.Model, BaseModel):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    token_type = db.Column(db.String(10), nullable=False)
    user_identity = db.Column(db.String(50), nullable=False)
    revoked = db.Column(db.Boolean, nullable=False)
    expires = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def json(self):
        return {
            'token_id': self.id,
            'jti': self.jti,
            'token_type': self.token_type,
            'user_identity': self.user_identity,
            'revoked': self.revoked,
            'expires': self.expires
        }

    def __init__(self, jti, token_type, user_identity, expires, revoked):
        self.jti = jti
        self.token_type = token_type
        self.user_identity = user_identity
        self.expires = expires
        self.revoked = revoked

    @classmethod
    def is_jti_blacklisted(cls, decrypted_token):
        try:
            token = cls.query.filter_by(jti=decrypted_token['jti']).first()
            return token.revoked
        except NoResultFound:
            return True
