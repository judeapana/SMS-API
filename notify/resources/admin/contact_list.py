from flask import request
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus.reqparse import RequestParser

from notify import flask_filter, pagination, db, ErrorCodes
from notify.models import ContactList, User
from notify.resources.admin import namespace
from notify.resources.utils import SearchParam, paginate_fields, search, base_fields
from notify.schema import ContactListSchema

mschema = ContactListSchema()

model = namespace.clone('Contact List', base_fields, {
    'user_id': fields.String(),
    'contact_name': fields.String(),
    'phone_number': fields.String(),
    'email_address': fields.String(),
    'active': fields.Boolean(),
})

parser = RequestParser(bundle_errors=True, trim=True)
parser.add_argument('user_id', required=True, type=str, location='json')
parser.add_argument('contact_name', required=True, type=str, location='json')
parser.add_argument('phone_number', required=True, type=str, location='json')
parser.add_argument('email_address', required=False, type=str, location='json')
parser.add_argument('active', required=True, type=bool, location='json')


class Search(Resource):

    @namespace.expect(search)
    def post(self):
        _search = flask_filter.search(ContactList, [request.json.get('filters')], ContactListSchema(many=True),
                                      order_by=request.json.get('order_by', 'created'))
        return pagination.paginate(_search, mschema, True,
                                   pagination_schema_hook=SearchParam(ContactList).paginate_fields_with_filter)


class ContactListLs(Resource):
    method_decorators = []

    def get(self):
        return pagination.paginate(ContactList, mschema, True, pagination_schema_hook=paginate_fields)

    @namespace.expect(model)
    def post(self):
        errors = []
        contact_list = ContactList()
        args = parser.parse_args(strict=True)
        mschema.load(data=args, session=db.session, instance=contact_list, unknown='exclude')
        user = User.query.get(args.user_id)
        if user.contact_list.filter(ContactList.contact_name == args.contact_name).first():
            errors.append(ErrorCodes.CONTACT_ALREADY_EXIST)
        if errors:
            return errors, 400
        contact_list.save()
        return mschema.dump(obj=contact_list)


@namespace.param('pk', description='primary key')
class ContactListDetail(Resource):

    @namespace.marshal_with(model)
    def get(self, pk):
        contact_list = ContactList.query.get_or_404(pk)
        return contact_list

    @namespace.expect(model)
    @namespace.marshal_with(model)
    def put(self, pk):
        contact_list = ContactList.query.get_or_404(pk)
        args = parser.parse_args()
        mschema.load(data=args, session=db.session, instance=contact_list, unknown='exclude')
        contact_list.save()
        return contact_list

    @namespace.response(204, 'contact list item deleted')
    def delete(self, pk):
        contact_list = ContactList.query.get_or_404(pk)
        return contact_list.delete(), 204


namespace.add_resource(Search, '/contact-list/search', endpoint='contact_list_search')
namespace.add_resource(ContactListLs, '/contact-list', endpoint='contact_list_ls')
namespace.add_resource(ContactListDetail, '/contact-list/<uuid:pk>', endpoint='contact_list')
