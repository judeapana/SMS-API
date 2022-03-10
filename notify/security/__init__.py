from flask_restplus import Namespace

namespace = Namespace('Authentication', description='auth users')
from . import login, forgot_pwd, logout, refresh, reset_pwd, register, verify
