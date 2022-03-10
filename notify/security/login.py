import phonenumbers
from flask import current_app
from flask_bcrypt import check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, get_jti
from flask_restplus import Resource, fields, abort
from flask_restplus.reqparse import RequestParser

from notify import redis
from notify.models import User
from notify.security import namespace

login_user_model = namespace.model('Login', {
    'username': fields.String(),
    'password': fields.String(),
})

parser = RequestParser(bundle_errors=True, trim=True)
parser.add_argument('username', type=str, location='json',
                    required=True, help='username is required')
parser.add_argument('password', type=str, location='json', required=True,
                    help='password is required')


class LoginUser(Resource):

    @namespace.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args(strict=True)
        try:
            number = phonenumbers.parse(args.username, 'GH').national_number
        except:
            number = args.username
        user = User.query.filter((User.email_address == args.username) | (User.phone_number == number)).first()
        if not user:
            return abort(401, 'Invalid credentials provided')
        else:
            if not check_password_hash(user.password, args.password):
                return abort(401, 'Invalid credentials provided')
            else:
                if not user.active:
                    return abort(401, 'Account not active')
                else:
                    access_token = create_access_token(identity=user.id)
                    refresh_token = create_refresh_token(identity=user.id)
                    jti = get_jti(access_token)
                    ref_jti = get_jti(refresh_token)
                    redis.set(jti, 0, ex=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'])
                    redis.set(ref_jti, 0, ex=current_app.config['JWT_REFRESH_TOKEN_EXPIRES'])
                    return {'token': {'main': access_token, 'refresh': refresh_token},
                            'user': {'username': user.username, 'role': user.role}}, 200


namespace.add_resource(LoginUser, '/', endpoint='login')
