from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_filter import FlaskFilter
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_otp import OTP
from flask_redis import FlaskRedis
from flask_rest_paginate import Pagination
from flask_rq2 import RQ
# from flask_sockets import Sockets
from flask_sqlalchemy import SQLAlchemy

flask_filter = FlaskFilter()
pagination = Pagination()

cors = CORS()
limiter = Limiter(key_func=get_ipaddr)
crypt = Bcrypt()
otp = OTP()
mail = Mail()
rq = RQ()
ma = Marshmallow()
redis = FlaskRedis()
# sockets = Sockets()
jwt = JWTManager()
migrate = Migrate()
db = SQLAlchemy()
