from flask import request
from flask_jwt_extended import current_user
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus.reqparse import RequestParser

from notify import flask_filter, pagination, db
from notify.models import ContactList
from notify.resources.user import namespace
from notify.resources.utils import SearchParam, paginate_fields, search, base_fields
from notify.schema import ContactListSchema

mschema = ContactListSchema()

model = namespace.clone('Contact List', base_fields, {
    'contact_name': fields.String(),
    'phone_number': fields.String(),
    'email_address': fields.String(),
    'active': fields.Boolean(),
})

parser = RequestParser(bundle_errors=True, trim=True)
parser.add_argument('contact_name', required=True, type=str, location='json')
parser.add_argument('phone_number', required=True, type=str, location='json')
parser.add_argument('email_address', required=False, type=str, location='json')
parser.add_argument('active', required=True, type=bool, location='json')


class Search(Resource):

    @namespace.expect(search)
    def post(self):
        _search = flask_filter.search(current_user.contact_list, [request.json.get('filters')],
                                      ContactListSchema(many=True),
                                      order_by=request.json.get('order_by', 'created'))
        return pagination.paginate(_search, mschema, True,
                                   pagination_schema_hook=SearchParam(
                                       current_user.contact_list).paginate_fields_with_filter)


class ContactListLs(Resource):

    def get(self):
        return pagination.paginate(current_user.contact_list, mschema, True, pagination_schema_hook=paginate_fields)

    @namespace.expect(model)
    @namespace.marshal_with(model, code=201)
    def post(self):
        contact_list = ContactList()
        args = parser.parse_args(strict=True)
        mschema.load(data=args, session=db.session, instance=contact_list, unknown='exclude')
        current_user.contact_list.append(contact_list)
        current_user.save()
        return contact_list


@namespace.param('pk', description='primary key')
class ContactListDetail(Resource):

    @namespace.marshal_with(model)
    def get(self, pk):
        contact_list = current_user.contact_list.filter(ContactList.id == pk).first_or_404()
        return contact_list

    @namespace.expect(model)
    @namespace.marshal_with(model)
    def put(self, pk):
        contact_list = current_user.contact_list.filter(ContactList.id == pk).first_or_404()
        args = parser.parse_args(strict=True)
        mschema.load(data=args, session=db.session, instance=contact_list, unknown='exclude')
        contact_list.save()
        return contact_list

    @namespace.response(204, 'contact list item deleted')
    def delete(self, pk):
        contact_list = current_user.contact_list.filter(ContactList.id == pk).first_or_404()
        return contact_list.delete(), 204


namespace.add_resource(Search, '/contact-list/search', endpoint='user_search_contact_list')
namespace.add_resource(ContactListLs, 'contact-list/s', endpoint='user_contact_lists')
namespace.add_resource(ContactListDetail, 'contact-list/<uuid:pk>', endpoint='user_contact_list_details')
