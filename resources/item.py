from flask_jwt import jwt_required
from flask_restful import Resource, reqparse
from models.user import UserModel
from models.item import ItemModel
from utils import notifications
from twilio.base.exceptions import TwilioRestException

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



    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {'message': 'Item not found'}, 404

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

    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
        return {'message': 'Item deleted'}

    def put(self, name):
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
    def get(self):
        return {'items': [x.json() for x in ItemModel.query.all()]}
