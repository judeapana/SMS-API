from flask_jwt_extended import jwt_required, get_jwt
from flask_restplus import Resource, abort

from notify import redis
from notify.security import namespace


class LogoutUser(Resource):
    method_decorators = [jwt_required()]

    def delete(self):
        jti = get_jwt().get('jti')
        redis.delete(jti)
        return abort(200)


namespace.add_resource(LogoutUser, '/logout', endpoint='logout')
