import random

import phonenumbers
from flask import json, current_app
from flask_restplus import Resource, inputs, fields
from flask_restplus.reqparse import RequestParser

from notify import User, ErrorCodes, redis
from notify.security import namespace

parser = RequestParser(bundle_errors=True, trim=True)

register_model = namespace.model('register', {
    'email_address': fields.String(),
    'phone_number': fields.String(),
    'password': fields.String()
})


class Register(Resource):
    method_decorators = []

    @namespace.expect(register_model)
    def post(self):
        parser.add_argument('email_address', type=inputs.email(), required=True, location='json')
        parser.add_argument('phone_number', required=True, type=str, location='json')
        parser.add_argument('password', required=True, type=str, location='json')
        args = parser.parse_args(strict=True)

        email = User.query.filter(User.email_address == args.email_address).first()
        if email:
            return ErrorCodes.EMAIL_TAKEN, 400
        number = phonenumbers.parse(args.phone_number, 'GH').national_number
        phone_number = User.query.filter(
            User.phone_number == number).first()
        if phone_number:
            return ErrorCodes.PHONE_NUMBER_TAKEN, 400
        otp = random.randint(1000, 9999)
        obj = {'type': 'VERIFY', 'otp': otp, 'email_address': args.email_address, 'phone_number': number,
               'password': args.password}
        encode = json.JSONEncoder().encode(obj)
        redis.set(otp, encode, ex=current_app.config['OTP_EXPIRES'] * 3)
        print(otp)
        return {'message': 'Creating account valid OTP'}


namespace.add_resource(Register, '/register', endpoint='register')
