from flask.json import JSONDecoder
from flask_restplus import Resource, fields
from flask_restplus.reqparse import RequestParser

from notify import crypt, redis, ErrorCodes
from notify.models import User
from notify.security import namespace

parser = RequestParser(bundle_errors=True, trim=True)

reset_pwd_model = namespace.model('reset_pwd', {
    'otp': fields.String(),
    'password': fields.String()
})


class ResetPwd(Resource):
    @namespace.expect(reset_pwd_model)
    def post(self):
        parser.add_argument('otp', required=True, location='json', type=str)
        parser.add_argument('password', required=True, location='json', type=str)
        args = parser.parse_args(strict=True)
        if not redis.get(args.otp):
            return ErrorCodes.OTP_INVALID, 400
        data = JSONDecoder().decode(redis.get(args.otp).decode())
        if data is None or data.get("type") != 'PWD':
            return ErrorCodes.OTP_INVALID, 400

        user = User.query.filter(User.phone_number == data.get('phone_number')).first()
        if not user:
            return {'message': 'User not found'}, 404
        user.password = crypt.generate_password_hash(args.password).decode('utf-8')
        user.save()
        redis.delete(args.otp)
        return {'message': 'Your password has been successfully reset'}, 200


namespace.add_resource(ResetPwd, '/reset-pwd', endpoint='reset_pwd')
