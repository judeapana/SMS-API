import random

import phonenumbers
from flask import current_app
from flask import json
from flask_restplus import Resource, fields
from flask_restplus.reqparse import RequestParser

from notify.exceptions import ErrorCodes
from notify.ext import limiter, redis
from notify.models import User
from notify.security import namespace

forgot_pwd_model = namespace.model('Forgot Password Model', {
    'phone_number': fields.String()
})

parser = RequestParser(bundle_errors=True, trim=True)
parser.add_argument('phone_number', required=True, type=str, location='json')


class ForgotPwd(Resource):

    @limiter.limit('10 per day')
    @namespace.expect(forgot_pwd_model)
    def post(self):
        args = parser.parse_args(strict=True)
        radn = random.randint(1000, 9999)
        number = phonenumbers.parse(args.phone_number, 'GH').national_number
        user = User.query.filter(
            (User.phone_number == number)).first()
        if not user:
            return ErrorCodes.PHONE_NUMBER_INVALID, 400
        obj = {'type': 'PWD', 'otp': radn, 'phone_number': number}
        encode = json.JSONEncoder().encode(obj)
        redis.set(radn, encode, ex=current_app.config['OTP_EXPIRES'])
        print(radn)
        return {'message': 'OTP has been sent to the phone number provided'}


namespace.add_resource(ForgotPwd, '/forgot-pwd', endpoint='forgot_pwd')
