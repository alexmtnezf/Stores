from werkzeug.security import safe_str_cmp

from models.user import UserModel


def authenticate(username, password):
    """
    Function that gets called when a client calls the /auth endpoint with
    their username and password
    :param username: User's username in string format
    :param password: User's password in string format
    :return: A UserModel object if the authentication is successful, None otherwise.
    """
    user = UserModel.find_by_username(username)
    if user and safe_str_cmp(user.password, password):
        return user
    return None


def identity(payload):
    """
    Function that gets the JWT in the request Authorization header, using Flask-JWT,
    if the token is verified that is correct, the user id is decoded and put in payload to get the UserModel object
    :param payload: A dictionary provided by Flask-JWT after the token has been decoded,
                    with 'identity' as key and value the user id.
    :return: A UserModel object
    """
    user_id = payload['identity']
    return UserModel.find_by_id(user_id)
