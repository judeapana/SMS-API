from flask_jwt_extended import get_jwt_identity, create_access_token, jwt_required
from flask_restplus import Resource

from notify.security import namespace


class RefreshLoginUser(Resource):

    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user, fresh=True)
        return {'token': {'main': access_token}}


namespace.add_resource(RefreshLoginUser, '/refresh', endpoint='refresh')
