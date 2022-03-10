import secrets

from flask.json import JSONDecoder
from flask_restplus import Resource, fields
from flask_restplus.reqparse import RequestParser

from notify import redis, ErrorCodes, crypt, User
from notify.models import Credit
from notify.security import namespace

parser = RequestParser(bundle_errors=True, trim=True)

verify_model = namespace.model('verify', {
    'otp': fields.String()
})


class Verify(Resource):

    def post(self):
        parser.add_argument('otp', required=True, location='json', type=str)
        args = parser.parse_args(strict=True)
        try:
            if not redis.get(args.otp):
                return ErrorCodes.OTP_INVALID, 400

            data = JSONDecoder().decode(redis.get(args.otp).decode())
            if data is None or data.get("type") != 'VERIFY':
                return ErrorCodes.OTP_INVALID, 400
            password = crypt.generate_password_hash(data.get('password')).decode('utf-8')
            username = f'{data.get("email_address").split("@")[0]}_{secrets.token_hex(5)}'

            user = User(email_address=data.get('email_address'), phone_number=data.get('phone_number'),
                        password=password, active=True, role='USER', username=username)
        except Exception as e:
            return {'message': "An error occurred"}, 500
        redis.delete(args.otp)
        user.credits.append(Credit(form='MAIN', unit=0))
        user.credits.append(Credit(form='BONUS', unit=3))
        user.save()
        return {'message': 'Your account has been successfully created'}, 200


namespace.add_resource(Verify, '/verify', endpoint='verify')
