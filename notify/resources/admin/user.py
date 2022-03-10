from flask import request
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus.reqparse import RequestParser

from notify import flask_filter, pagination, db, crypt, ErrorCodes
from notify.models import User
from notify.resources.admin import namespace
from notify.resources.utils import SearchParam, paginate_fields, search, base_fields
from notify.schema import UserSchema
from notify.tasks.mailing import send_notification

mschema = UserSchema()

model = namespace.clone('User', base_fields, {
    'username': fields.String(),
    'email_address': fields.String(),
    'phone_number': fields.String(),
    'role': fields.String(),
    'account_type': fields.String(),
    'last_logged_in': fields.DateTime(),
    'active': fields.Boolean(),
})

parser = RequestParser(bundle_errors=True, trim=True)
parser.add_argument('username', required=True, type=str, location='json')
parser.add_argument('password', required=True, type=str, location='json')
parser.add_argument('email_address', required=True, type=str, location='json')
parser.add_argument('phone_number', required=True, type=str, location='json')
parser.add_argument('role', required=True, type=str, location='json')
parser.add_argument('account_type', required=False, type=str, location='json')
parser.add_argument('active', required=True, type=bool, location='json')


class Search(Resource):

    @namespace.expect(search)
    def post(self):
        _search = flask_filter.search(User, [request.json.get('filters')], UserSchema(many=True),
                                      order_by=request.json.get('order_by', 'created'))
        return pagination.paginate(_search, mschema, True,
                                   pagination_schema_hook=SearchParam(User).paginate_fields_with_filter)


class UserList(Resource):

    def get(self):
        rqp = RequestParser(trim=True)
        rqp.add_argument('all', location='args', type=bool)
        args = rqp.parse_args()
        if args.all:
            return mschema.dump(obj=User.query.all(), many=True)

        return pagination.paginate(User, mschema, True, pagination_schema_hook=paginate_fields)

    @namespace.expect(model)
    # @namespace.marshal_with(model, code=201)
    def post(self):
        user = User()
        args = parser.parse_args(strict=True)
        duser = User.query.filter(User.username == args.username).first()
        errors = []
        if duser:
            errors.append(ErrorCodes.USER_ALREADY_EXIST)
        duser = User.query.filter(User.email_address == args.email_address).first()
        if duser:
            errors.append(ErrorCodes.EMAIL_TAKEN)

        duser = User.query.filter(User.phone_number == args.phone_number).first()
        if duser:
            errors.append(ErrorCodes.PHONE_NUMBER_TAKEN)
        if errors:
            return errors, 400
        mschema.load(data=args, session=db.session, instance=user, unknown='exclude')
        user.password = crypt.generate_password_hash(args.password).decode('utf-8')
        message = f"""
        <h4>Your Account was created</h4> 
        <p>Your username is {args.username}</p>
        <p>Your Account has been created your password is {args.password}</p>
        <p>Thank you.</p>
        """
        send_notification.queue("Account Created", message, args.email_address)
        return user.save(), 200


@namespace.param('pk', description='primary key')
class UserDetail(Resource):

    @namespace.marshal_with(model)
    def get(self, pk):
        user = User.query.get_or_404(pk)
        return user

    @namespace.expect(model)
    def put(self, pk):
        errors = []
        user = User.query.get_or_404(pk)
        parser.remove_argument('password')
        args = parser.parse_args()
        duser = User.query.filter(User.username == args.username, User.id != pk).first()
        if duser:
            errors.append(ErrorCodes.USER_ALREADY_EXIST)
        duser = User.query.filter(User.email_address == args.email_address, User.id != pk).first()
        if duser:
            errors.append(ErrorCodes.EMAIL_TAKEN)

        duser = User.query.filter(User.phone_number == args.phone_number, User.id != pk).first()
        if duser:
            errors.append(ErrorCodes.PHONE_NUMBER_TAKEN)
        if errors:
            return errors, 400
        mschema.load(data=args, session=db.session, instance=user, unknown='exclude')
        user.save()
        return mschema.dump(obj=user)

    @namespace.response(204, 'User deleted')
    def delete(self, pk):
        user = User.query.get_or_404(pk)
        return user.delete(), 204


namespace.add_resource(Search, '/users/search', endpoint='user_search')
namespace.add_resource(UserList, '/users', endpoint='users')
namespace.add_resource(UserDetail, '/user/<uuid:pk>', endpoint='user')
