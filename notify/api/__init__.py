from flask import Blueprint
from flask_restplus import Api

from notify.resources.admin import namespace as admin
from notify.resources.user import namespace as user
from notify.resources.utils import namespace as base
from notify.security.login import namespace as login

notify_api = Blueprint('notify', __name__)
api = Api(notify_api, title='Notify')
api.add_namespace(base)
api.add_namespace(login, '/auth')
api.add_namespace(admin, '/admin')
api.add_namespace(user, '/user')
