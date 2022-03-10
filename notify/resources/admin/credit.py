from flask import request
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus.reqparse import RequestParser

from notify import flask_filter, pagination, db
from notify.models import Credit
from notify.resources.admin import namespace
from notify.resources.utils import SearchParam, paginate_fields, search, base_fields
from notify.schema import CreditSchema

mschema = CreditSchema()

model = namespace.clone('Credit', base_fields, {
    'user_id': fields.String(),
    'name': fields.String(),
    'form': fields.String(),
    'unit': fields.Integer(),
})

parser = RequestParser(bundle_errors=True, trim=True)
parser.add_argument('user_id', required=True, type=str, location='json')
parser.add_argument('form', required=True, type=str, location='json')
parser.add_argument('unit', required=True, type=int, location='json')


class Search(Resource):

    @namespace.expect(search)
    def post(self):
        _search = flask_filter.search(Credit, [request.json.get('filters')], CreditSchema(many=True),
                                      order_by=request.json.get('order_by', 'created'))
        return pagination.paginate(_search, mschema, True,
                                   pagination_schema_hook=SearchParam(Credit).paginate_fields_with_filter)


class CreditList(Resource):
    method_decorators = []

    def get(self):
        return pagination.paginate(Credit, mschema, True, pagination_schema_hook=paginate_fields)

    @namespace.expect(model)
    @namespace.marshal_with(model, code=201)
    def post(self):
        credit = Credit()
        args = parser.parse_args(strict=True)
        mschema.load(data=args, session=db.session, instance=credit, unknown='exclude')
        credit.save()
        return credit


@namespace.param('pk', description='primary key')
class CreditDetail(Resource):

    @namespace.marshal_with(model)
    def get(self, pk):
        credit = Credit.query.get_or_404(pk)
        return credit

    @namespace.expect(model)
    @namespace.marshal_with(model)
    def put(self, pk):
        credit = Credit.query.get_or_404(pk)
        args = parser.parse_args(strict=True)
        mschema.load(data=args, session=db.session, instance=credit, unknown='exclude')
        credit.save()
        return credit

    @namespace.response(204, 'Credit year deleted')
    def delete(self, pk):
        credit = Credit.query.get_or_404(pk)
        return credit.delete(), 204


namespace.add_resource(Search, '/credits/search', endpoint='credit_search')
namespace.add_resource(CreditList, '/credit', endpoint='credits')
namespace.add_resource(CreditDetail, '/credits/<uuid:pk>', endpoint='credit')
