from flask import request
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus.reqparse import RequestParser

from notify import flask_filter, pagination, db
from notify.models import NicheAchieve
from notify.resources.admin import namespace
from notify.resources.utils import SearchParam, paginate_fields, search, base_fields
from notify.schema import NicheAchieveSchema

mschema = NicheAchieveSchema()

model = namespace.clone('NicheAchieve', base_fields, {
    'interest': fields.String(),
    'description': fields.String(),
    'active': fields.String(),
})

parser = RequestParser(bundle_errors=True, trim=True)
parser.add_argument('interest', required=True, type=str, location='json')
parser.add_argument('description', required=True, type=str, location='json')
parser.add_argument('active', required=True, type=bool, location='json')


class Search(Resource):

    @namespace.expect(search)
    def post(self):
        _search = flask_filter.search(NicheAchieve, [request.json.get('filters')], NicheAchieveSchema(many=True),
                                      order_by=request.json.get('order_by', 'created'))
        return pagination.paginate(_search, mschema, True,
                                   pagination_schema_hook=SearchParam(NicheAchieve).paginate_fields_with_filter)


class NicheAchieveList(Resource):

    def get(self):
        return pagination.paginate(NicheAchieve, mschema, True, pagination_schema_hook=paginate_fields)

    @namespace.expect(model)
    @namespace.marshal_with(model, code=201)
    def post(self):
        niche_achieve = NicheAchieve()
        args = parser.parse_args(strict=True)
        mschema.load(data=args, session=db.session, instance=niche_achieve, unknown='exclude')
        niche_achieve.save()
        return niche_achieve


@namespace.param('pk', description='primary key')
class NicheAchieveDetail(Resource):

    @namespace.marshal_with(model)
    def get(self, pk):
        niche_achieve = NicheAchieve.query.get_or_404(pk)
        return niche_achieve

    @namespace.expect(model)
    @namespace.marshal_with(model)
    def put(self, pk):
        niche_achieve = NicheAchieve.query.get_or_404(pk)
        args = parser.parse_args(strict=True)
        mschema.load(data=args, session=db.session, instance=niche_achieve, unknown='exclude')
        niche_achieve.save()
        return niche_achieve

    @namespace.response(204, 'Niche deleted')
    def delete(self, pk):
        niche_achieve = NicheAchieve.query.get_or_404(pk)
        return niche_achieve.delete(), 204


namespace.add_resource(Search, '/niche-achieves/search', endpoint='niche_achieve_search')
namespace.add_resource(NicheAchieveList, '/niche-achieves', endpoint='niche_achieves')
namespace.add_resource(NicheAchieveDetail, '/niche-achieve/<uuid:pk>', endpoint='niche_achieve')
