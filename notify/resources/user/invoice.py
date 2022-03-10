from flask_jwt_extended import current_user
from flask_restplus import Resource
from flask_restplus import fields

from notify import pagination
from notify.models import Invoice
from notify.resources.user import namespace
from notify.resources.utils import paginate_fields, base_fields
from notify.schema import InvoiceSchema

mschema = InvoiceSchema()

model = namespace.clone('Invoice', base_fields, {
    "transaction": fields.String(),
    "amount_paid": fields.String(),
    "payment_mode": fields.String(),
    "status": fields.String(),
    "note": fields.String(),
})


class InvoiceList(Resource):

    def get(self):
        return pagination.paginate(current_user.invoices, mschema, True, pagination_schema_hook=paginate_fields)


@namespace.param('pk', description='primary key')
class InvoiceDetail(Resource):

    @namespace.marshal_with(model)
    def get(self, pk):
        invoice = current_user.invoices.filter_by(Invoice.id == pk).first_or_404()
        return invoice


namespace.add_resource(InvoiceList, '/invoices', endpoint='user_invoices')
namespace.add_resource(InvoiceDetail, '/invoice/<uuid:pk>', endpoint='user_invoice')
