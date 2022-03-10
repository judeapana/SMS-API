from flask import request
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus.reqparse import RequestParser

from notify import flask_filter, pagination, db
from notify.models import Transaction, User, Invoice, Credit
from notify.resources.admin import namespace
from notify.resources.utils import SearchParam, paginate_fields, search, base_fields
from notify.schema import TransactionSchema

mschema = TransactionSchema()

model = namespace.clone('Transaction', base_fields, {
    'user_id': fields.String(),
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
        _search = flask_filter.search(Transaction, [request.json.get('filters')],
                                      TransactionSchema(many=True),
                                      order_by=request.json.get('order_by', 'created'))
        return pagination.paginate(_search, mschema, True,
                                   pagination_schema_hook=SearchParam(Transaction).paginate_fields_with_filter)


class TransactionList(Resource):

    def get(self):
        return pagination.paginate(Transaction, mschema, True, pagination_schema_hook=paginate_fields)


@namespace.param('pk', description='primary key')
class TransactionDetail(Resource):

    @namespace.marshal_with(model)
    def get(self, pk):
        template = Transaction.query.filter(Transaction.id == pk).first_or_404()
        return template


class FlutterwaveWatcher(Resource):
    """
    watches for incoming transactions
    """

    def post(self):
        pay = RequestParser(trim=True)
        pay.add_argument('event', type=str, location='json')
        pay.add_argument('email', type=str, location='json')
        pay.add_argument('txRef', type=str, location='json')
        pay.add_argument('orderRef', type=str, location='json')
        pay.add_argument('app_fee', type=float, location='json')
        pay.add_argument('charged_amount', type=float, location='json')
        pay.add_argument('phone_number', type=float, location='json')
        pay.add_argument('currency', type=str, location='json')
        pay.add_argument('amount', type=float, location='json')
        pay.add_argument('status', type=float, location='json')
        pay.add_argument('message', type=float, location='json')
        args = pay.parse_args()
        user = User.query.filter((User.email_address == args.email) | (User.phone_number == args.phone_number)).first()
        transaction = Transaction()
        if user:
            if args.event == 'charge.complete':
                mschema.load(data=args, session=db.session, instance=transaction, unknown='exclude')
                invoice = Invoice(user=user, amount=args.amount, status=args.status, note=args.message)
                current_credit = user.credits.filter(Credit.form == 'MAIN').first()
                current_credit.unit += invoice.credit_amt
                current_credit.save()
                transaction.invoice.append(invoice)
                mschema.save(), 200
            else:
                mschema.load(data=args, session=db.session, instance=transaction, unknown='exclude')
                mschema.save(), 200
        return False


namespace.add_resource(Search, '/transaction/watcher', endpoint='transaction_watcher')
namespace.add_resource(Search, '/transaction/search', endpoint='transaction_search')
namespace.add_resource(TransactionList, '/transactions', endpoint='transactions')
namespace.add_resource(TransactionDetail, '/transaction/<uuid:pk>', endpoint='transaction')
