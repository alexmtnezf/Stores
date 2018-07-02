# -*- coding: utf-8 -*-
from datetime import datetime

from flask_jwt_extended import decode_token
from sqlalchemy.orm.exc import NoResultFound

from db import db
from exception import TokenNotFound
from models.token import TokenModel


def _epoch_utc_to_datetime(epoch_utc):
    """
    Helper function for converting epoch timestamps (as stored in JWTs) into
    python datetime objects (which are easier to use with sqlalchemy).
    """
    return datetime.utcfromtimestamp(epoch_utc)


def add_token_to_database(encoded_token, identity_claim):
    """
    Adds a new token to the database. It is not revoked when it is added.
    :param identity_claim:
    """
    decoded_token = decode_token(encoded_token)
    jti = decoded_token['jti']
    token_type = decoded_token['type']
    user_identity = decoded_token[identity_claim]
    expires = _epoch_utc_to_datetime(decoded_token['exp'])
    revoked = False

    db_token = TokenModel(
        jti=jti,
        token_type=token_type,
        user_identity=user_identity,
        expires=expires,
        revoked=revoked,
    )
    # Save the token to database
    db_token.save_to_db()


def is_token_revoked(decoded_token):
    """
    Checks if the given token is revoked or not. Because we are adding all the
    tokens that we create into this database, if the token is not present
    in the database we are going to consider it revoked, as we don't know where
    it was created.
    """
    jti = decoded_token['jti']
    try:
        token = TokenModel.find_by(jti=jti).one()
        return token.revoked
    except NoResultFound:
        return True


def get_user_tokens(user_identity):
    """
    Returns all of the tokens, revoked and unrevoked, that are stored for the
    given user
    """
    return TokenModel.find_by(user_identity=user_identity).all()


def revoke_token(jti, identity):
    """
    Revokes the given token. Raises a TokenNotFound error if the token does
    not exist in the database
    """
    try:
        token = TokenModel.find_by(jti=jti, user_identity=identity).one()
        token.revoked = True
        token.save_to_db()
    except NoResultFound:
        raise TokenNotFound("Could not find the token {}".format(jti))


def unrevoke_token(token_id, user):
    """
    Unrevokes the given token. Raises a TokenNotFound error if the token does
    not exist in the database
    """
    try:
        token = TokenModel.find_by(id=token_id, user_identity=user).one()
        token.revoked = False
        token.save_to_db()
    except NoResultFound:
        raise TokenNotFound("Could not find the token {}".format(token_id))


def prune_database():
    """
    Delete tokens that have expired from the database.
    How (and if) you call this is entirely up you. You could expose it to an
    endpoint that only administrators could call, you could run it as a cron,
    set it up with flask cli, etc.
    """
    now = datetime.now()
    expired = TokenModel.query.filter(TokenModel.expires < now).all()
    for token in expired:
        db.session.delete(token)
    db.session.commit()
