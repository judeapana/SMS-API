from flask_jwt_extended import current_user
from flask_restplus import Resource
from flask_restplus import fields

from notify import pagination
from notify.models import Credit
from notify.resources.user import namespace
from notify.resources.utils import paginate_fields, base_fields
from notify.schema import CreditSchema

mschema = CreditSchema()

model = namespace.clone('Credit', base_fields, {
    'name': fields.String(),
    'form': fields.String(),
    'unit': fields.Integer(),
})


class CreditList(Resource):
    method_decorators = []

    def get(self):
        return pagination.paginate(current_user.credits, mschema, True, pagination_schema_hook=paginate_fields)


@namespace.param('pk', description='primary key')
class CreditDetail(Resource):

    @namespace.marshal_with(model)
    def get(self, pk):
        credit = current_user.credits.filter(Credit.id == pk).first_or_404()
        return credit


namespace.add_resource(CreditList, '/credits', endpoint='user_credits')
namespace.add_resource(CreditDetail, '/credit/<uuid:pk>', endpoint='user_credit')
