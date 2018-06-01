"""
UserRegister

Allows the user to register, so the only http verb used in this resource is post method
"""
from flask_restful import Resource, reqparse

from models.user import UserModel


class UserRegister(Resource):
    """
    This resources allows users to register (sign up) by sending their username and password in
    a POST request
    """

    # Class variable for parsing the request arguments (no matter the HTTP method, such as POST, GET, PUT)
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help='This name cannot be blank')
    parser.add_argument('username', type=str, required=True, help='This username cannot be blank')
    parser.add_argument('password', type=str, required=True, help="This password cannot be blank.")

    def post(self):
        data = UserRegister.parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {"message": "A user with that username already exists"}, 400

        user = UserModel(**data)
        try:
            user.save_to_db()
        except:
            return {"message": "An error occurred creating the store."}, 500

        return {"message": "User created successfully."}, 201
