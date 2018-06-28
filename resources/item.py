"""
resources/item.py

Module that contains api resources regarding items information management.
"""
from flask_jwt_extended import jwt_required, jwt_optional, get_jwt_identity, fresh_jwt_required, get_jwt_claims
from flask_restful import Resource, reqparse
from twilio.base.exceptions import TwilioRestException

from models.item import ItemModel
from models.user import UserModel
from utils import notifications


class ItemResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help="This field cannot be left blank!")

    parser.add_argument('store_id',
                        type=int,
                        required=True,
                        help="Every item needs a store!")

    @jwt_required
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {'message': 'Item not found'}, 404

    @jwt_required
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': "An item with name '{}' already exists.".format(name)}, 400

        ItemResource.parser.add_argument('user_id',
                        type=int,
                        required=True,
                        help="User id is required!")

        data = ItemResource.parser.parse_args()


        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except:
            return {"message": "An error occurred inserting the item."}, 500

        current_user = UserModel.find_by_id(data['user_id'])
        try:
            notifications.NotificationDispatcher.send_sms(
                from_name=current_user.username,
                to_phone='+12106105564',
                to_name='Alex',
                text='New Item with name {} and price {} was added.'.format(item.name, item.price))
        except TwilioRestException as ex:
            return {'message': ex.msg}, 500

        return item.json(), 201

    @fresh_jwt_required
    def delete(self, name):
        """This endpoint is used to delete an item from the store.
        Requires a fresh jwt token to execute the request
        ---
        tags:
          - Items
        parameters:
          - in: path
            name: name
            required: true
            description: The name of the item, try item1!
            type: string
        responses:
          200:
            description: Item deleted
          401:
            description: Authorization required
          403:
            description: Admin privilege required

        """
        # Checking claims for actually execute or not the request as expected
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required'}, 403

        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
        return {'message': 'Item deleted'}

    @jwt_required
    def put(self, name):
        """
        This is an example
        ---
        tags:
          - Items
        parameters:
          - in: body
            name: body
            schema:
              $ref: '#/definitions/Item'
          - in: path
            name: name
            required: true
            description: The name of the item!
            type: string
        responses:
          201:
            description: The item has been created
            schema:
              $ref: '#/definitions/Item'
          200:
            description: The task has been updated
            schema:
              $ref: '#/definitions/Item'
        """
        data = ItemResource.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, **data)
        else:
            item.price = data['price']

        try:
            item.save_to_db()
        except:
            return {"message": "An error occurred inserting the item."}, 500

        return item.json()


class ItemListResource(Resource):
    @jwt_optional
    def get(self):
        """
        Returns the list of items in the store
        ---
        tags:
          - Items
        definitions:
          Item:
            type: object
            properties:
              id:
                type: integer
                description: Identifier of the Item
              name:
                type: string
                description: Name of the item
              store_id:
                type: integer
                description: Identifier of the store to which this item belongs
        responses:
          200:
            description: The list of items in the store
            schema:
              type: object
              properties:
                items:
                  type: array
                  items:
                    $ref: '#/definitions/Item'
            examples:
              { 'items' : [{'id': 1, 'name': 'New Item', 'store_id': 2},]}
        """

        # Access the identity of the current user identity (username) with get_jwt_identity
        current_user = get_jwt_identity()
        # same as: {'items': list(map(lambda x: x.json(), ItemModel.query.all()))}
        items = [item.json() for item in ItemModel.find_all()]
        if current_user:
            return {'items': items}

        return {
            'items': list(map(lambda x: x['name'], items)),
            'message': 'More data available if logged in'
        }
