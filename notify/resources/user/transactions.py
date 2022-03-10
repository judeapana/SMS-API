from flask import request
from flask_jwt_extended import current_user
from flask_restplus import Resource
from flask_restplus import fields

from notify import flask_filter, pagination
from notify.models import Template
from notify.resources.user import namespace
from notify.resources.utils import SearchParam, paginate_fields, search, base_fields
from notify.schema import TemplateSchema, TransactionSchema

mschema = TransactionSchema()

model = namespace.clone('Transaction', base_fields, {
    'invoice': fields.String(),
    'txRef': fields.String(),
    'orderRef': fields.String(),
    'app_fee': fields.String(),
    'charged_amount': fields.String(),
    'currency': fields.String(),
    'amount': fields.String(),
    'status': fields.String(),

})


class Search(Resource):

    @namespace.expect(search)
    def post(self):
        _search = flask_filter.search(current_user.transactions, [request.json.get('filters')],
                                      TemplateSchema(many=True),
                                      order_by=request.json.get('order_by', 'created'))
        return pagination.paginate(_search, mschema, True,
                                   pagination_schema_hook=SearchParam(
                                       current_user.transactions).paginate_fields_with_filter)


class TransactionList(Resource):

    def get(self):
        return pagination.paginate(current_user.templates, mschema, True, pagination_schema_hook=paginate_fields)


@namespace.param('pk', description='primary key')
class TransactionDetail(Resource):

    @namespace.marshal_with(model)
    def get(self, pk):
        template = current_user.templates.filter(Template.id == pk).first_or_404()
        return template


namespace.add_resource(Search, '/transaction/search', endpoint='user_transaction_search')
namespace.add_resource(TransactionList, '/transaction', endpoint='user_transactions')
namespace.add_resource(TransactionDetail, '/transaction/<uuid:pk>', endpoint='user_transaction')
