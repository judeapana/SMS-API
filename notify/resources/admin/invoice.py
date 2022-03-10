from flask import request
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus.reqparse import RequestParser

from notify import flask_filter, pagination, db
from notify.models import Invoice, Credit
from notify.resources.admin import namespace
from notify.resources.utils import SearchParam, paginate_fields, search, base_fields
from notify.schema import InvoiceSchema

mschema = InvoiceSchema()

model = namespace.clone('Invoice', base_fields, {
    'user_id': fields.String(),
    "amount_paid": fields.String(),
    "payment_mode": fields.String(),
    "status": fields.String(),
    "note": fields.String(),
})

parser = RequestParser(bundle_errors=True, trim=True)
parser.add_argument('user_id', required=True, type=str, location='json')
parser.add_argument('credit_id', required=True, type=str, location='json')
parser.add_argument('amount_paid', required=True, type=float, location='json')
parser.add_argument('payment_mode', required=True, type=str, location='json')
parser.add_argument('status', required=True, type=bool, location='json')
parser.add_argument('note', required=True, type=str, location='json')


class Search(Resource):

    @namespace.expect(search)
    def post(self):
        _search = flask_filter.search(Invoice, [request.json.get('filters')], InvoiceSchema(many=True),
                                      order_by=request.json.get('order_by', 'created'))
        return pagination.paginate(_search, mschema, True,
                                   pagination_schema_hook=SearchParam(Invoice).paginate_fields_with_filter)


class InvoiceList(Resource):

    def get(self):
        return pagination.paginate(Invoice, mschema, True, pagination_schema_hook=paginate_fields)

    @namespace.expect(model)
    @namespace.marshal_with(model, code=201)
    def post(self):
        invoice = Invoice()
        args = parser.parse_args(strict=True)
        mschema.load(data=args, session=db.session, instance=invoice, unknown='exclude')
        invoice.credit.append(Credit(user_id=args.user_id, form='MAIN', unit=invoice.credit_amt))
        invoice.save()
        return invoice


@namespace.param('pk', description='primary key')
class InvoiceDetail(Resource):

    @namespace.marshal_with(model)
    def get(self, pk):
        invoice = Invoice.query.get_or_404(pk)
        return invoice

    @namespace.response(204, 'Invoice deleted')
    def delete(self, pk):
        invoice = Invoice.query.get_or_404(pk)
        return invoice.delete(), 204


namespace.add_resource(Search, '/invoices/search', endpoint='invoice_search')
namespace.add_resource(InvoiceList, '/invoices', endpoint='invoices')
namespace.add_resource(InvoiceDetail, '/invoices/<uuid:pk>', endpoint='invoice')
