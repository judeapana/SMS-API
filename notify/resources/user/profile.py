import random
from json import JSONDecoder

from flask import json, current_app
from flask_jwt_extended import current_user
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus.reqparse import RequestParser

from notify import db, redis, ErrorCodes, crypt
from notify.resources.user import namespace
from notify.resources.utils import base_fields
from notify.schema import UserSchema

mschema = UserSchema()

model = namespace.clone('User', base_fields, {
    'username': fields.String(),
    'email_address': fields.String(),
    'phone_number': fields.String(),
    'account_type': fields.String(),
    'last_logged_in': fields.DateTime(),
    'active': fields.Boolean(),
})

parser = RequestParser(bundle_errors=True, trim=True)
parser.add_argument('password', required=True, type=str, location='json')
parser.add_argument('email_address', required=True, type=str, location='json')
parser.add_argument('phone_number', required=True, type=str, location='json')
parser.add_argument('account_type', required=False, type=str, location='json')
parser.add_argument('active', required=True, type=bool, location='json')


class UserPhoneNumber(Resource):
    def post(self):
        phone = RequestParser(trim=True)
        phone.add_argument('new_phone_number', required=True, type=str, location='json')
        otp = random.randint(1000, 9999)
        args = phone.parse_args(strict=True)
        obj = {
            'new_phone_number': args.new_phone_number,
        }
        encode = json.JSONEncoder().encode(obj)
        redis.set(otp, encode, ex=current_app.config['OTP_EXPIRES'] * 3)
        return

    def put(self):
        phone = RequestParser(trim=True)
        phone.add_argument('otp', required=True, type=str, location='json')
        args = parser.parse_args()
        try:
            if not redis.get(args.otp):
                return ErrorCodes.OTP_INVALID, 400

            data = JSONDecoder().decode(redis.get(args.otp).decode())
            if data is None or not data.get("new_phone_number"):
                return ErrorCodes.OTP_INVALID, 400
            current_user.phone_number = data.get("new_phone_number")
            current_user.save()
        except Exception as e:
            return 'Error Occurred', 500


class UserPassword(Resource):
    def post(self):
        phone = RequestParser(trim=True)
        phone.add_argument('new_password', required=True, type=str, location='json')
        otp = random.randint(1000, 9999)
        args = phone.parse_args(strict=True)
        obj = {
            'new_password': args.new_password,
        }
        encode = json.JSONEncoder().encode(obj)
        redis.set(otp, encode, ex=current_app.config['OTP_EXPIRES'] * 3)

    def put(self):
        phone = RequestParser(trim=True)
        phone.add_argument('otp', required=True, type=str, location='json')
        args = parser.parse_args()
        try:
            if not redis.get(args.otp):
                return ErrorCodes.OTP_INVALID, 400

            data = JSONDecoder().decode(redis.get(args.otp).decode())
            if data is None or not data.get("new_password"):
                return ErrorCodes.OTP_INVALID, 400
            current_user.password = crypt.generate_password_hash(data.get("new_password")).decode('utf-8')
            current_user.save()
        except Exception as e:
            return 'Error Occurred', 500


class UserDetail(Resource):

    @namespace.marshal_with(model)
    def get(self):
        return current_user

    @namespace.expect(model)
    @namespace.marshal_with(model)
    def put(self):
        account = RequestParser(trim=True)
        account.add_argument('email_address', required=True, location='json')
        account.add_argument('account_type', required=True, location='json')
        args = account.parse_args(strict=True)
        mschema.load(data=args, session=db.session, instance=current_user, unknown='exclude')
        current_user.save()
        return current_user


namespace.add_resource(UserDetail, '/profile', endpoint='user_profile')
namespace.add_resource(UserPhoneNumber, '/change-ph', endpoint='user_change_ph')
namespace.add_resource(UserPassword, '/change-pwd', endpoint='change_pwd')
