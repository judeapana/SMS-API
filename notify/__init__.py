from flask import Flask

from notify.config import Development
from notify.exceptions import ErrorCodes
from notify.ext import otp, mail, rq, ma, redis, jwt, migrate, crypt, limiter, cors, flask_filter, pagination
from notify.models import db, User


def create_app(_config=Development):
    app = Flask(__name__)
    cors.init_app(app, resources={r"/*": {"origins": "*"}})
    app.config.from_object(_config)
    db.init_app(app)
    pagination.init_app(app, db)
    otp.init_app(app)
    rq.init_app(app)
    ma.init_app(app)
    redis.init_app(app)
    app.register_blueprint(notify_api)
    # sockets.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    crypt.init_app(app)
    limiter.init_app(app)
    flask_filter.init_app(app)

    @jwt.token_in_blocklist_loader
    def check_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        token = redis.get(jti)
        return token is None

    @jwt.expired_token_loader
    def expired_callback(jwt_header, jwt_payload):
        return ErrorCodes.TOKEN_EXPIRED, 401

    @jwt.unauthorized_loader
    def unauthorized_callback(*args, **kwargs):
        return ErrorCodes.UNAUTHORIZED, 401

    @jwt.user_lookup_loader
    def user_loader(jwt_header, jwt_payload):
        identity = jwt_payload.get('sub')
        return User.query.filter(User.id == identity).one_or_none()

    return app


from notify.api import notify_api
