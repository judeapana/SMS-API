from functools import wraps

from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask_restplus import abort
from flask_restplus._http import HTTPStatus
from sqlalchemy import exc

from notify.ext import db


class Record:
    query = None

    @classmethod
    def validate_unique_post(cls, unique: list, payload: dict):
        message = []
        for key in unique:
            if cls.query.filter(getattr(cls, key) == payload.get(key)).first():
                db.session.rollback()
                message.append({key: 'already exist'})
        if message is not None:
            abort(HTTPStatus.CONFLICT, 'Input payload has conflicts', errors=message)
            # raise DbConflict(message=message)

    @classmethod
    def validate_unique_patch(cls, obj, unique: list, payload: dict):
        with db.session.no_autoflush:
            message = []
            for key in unique:
                if cls.query.filter(getattr(cls, 'id') != obj.id, getattr(cls, key) == payload.get(key)).first():
                    message.append({key: 'already exist'})
            if message is not None:
                abort(HTTPStatus.CONFLICT, errors=message)
                # raise DbConflict(message=message)

    def save(self, validate_post=False, validate_put=False, **kwargs):
        if validate_post:
            self.validate_unique_post(**kwargs)
        if validate_put:
            self.validate_unique_patch(self, **kwargs)
        try:
            db.session.add(self)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            print(e)
            db.session.rollback()

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()


# def role_required():
#     def wrapper(func):
#         @wraps(func)
#         def decorated(*args, **kwargs):
#             verify_jwt_in_request()
#             jti = get_jwt()
#             if jti['role'] == 'ADMIN':
#                 return func(*args, **kwargs)
#             else:
#                 return abort(403, 'Unauthorized Access')
#
#         return decorated
#
#     return wrapper

def role_required(roles):
    def wrapper(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            verify_jwt_in_request()
            jti = get_jwt()
            if jti['role'] not in roles:
                return abort(403, 'Unauthorized access')
            else:
                return func(*args, **kwargs)

        return decorated

    return wrapper
