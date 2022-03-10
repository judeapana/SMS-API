from flask import request
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus.reqparse import RequestParser

from notify import flask_filter, pagination, db, ErrorCodes
from notify.models import Campus
from notify.resources.admin import namespace
from notify.resources.utils import SearchParam, paginate_fields, search, base_fields
from notify.schema import CampusSchema

mschema = CampusSchema()

model = namespace.clone('Campus', base_fields, {
    'name': fields.String(),
    'university_id': fields.String(),
    'description': fields.String(),
})

parser = RequestParser(bundle_errors=True, trim=True)
parser.add_argument('name', required=True, type=str, location='json')
parser.add_argument('university_id', required=True, type=str, location='json')
parser.add_argument('description', required=False, type=str, location='json')


class Search(Resource):

    @namespace.expect(search)
    def post(self):
        _search = flask_filter.search(Campus, [request.json.get('filters')], CampusSchema(many=True),
                                      order_by=request.json.get('order_by', 'created'))
        return pagination.paginate(_search, mschema, True,
                                   pagination_schema_hook=SearchParam(Campus).paginate_fields_with_filter)


class CampusList(Resource):
    # @role_required()
    def get(self):
        rqp = RequestParser(trim=True)
        rqp.add_argument('all', location='args', type=bool)
        args = rqp.parse_args()
        if args.all:
            return mschema.dump(obj=Campus.query.all(), many=True)
        return pagination.paginate(Campus, mschema, True, pagination_schema_hook=paginate_fields)

    @namespace.expect(model)
    # @namespace.marshal_with(model, code=201)
    def post(self):
        errors = []
        campus = Campus()
        args = parser.parse_args(strict=True)
        if Campus.query.filter(Campus.name == args.name).first():
            errors.append(ErrorCodes.CAMPUS_ALREADY_EXIST)
        if errors:
            return errors, 400
        mschema.load(data=args, session=db.session, instance=campus, unknown='exclude')
        campus.save()
        return mschema.dump(obj=campus)


@namespace.param('pk', description='primary key')
class CampusDetail(Resource):

    @namespace.marshal_with(model)
    def get(self, pk):
        campus = Campus.query.get_or_404(pk)
        return campus

    @namespace.expect(model)
    @namespace.marshal_with(model)
    def put(self, pk):
        campus = Campus.query.get_or_404(pk)
        args = parser.parse_args()
        if Campus.query.filter(Campus.name == args.name, Campus.id != pk).first():
            return ErrorCodes.CAMPUS_ALREADY_EXIST, 400
        mschema.load(data=args, session=db.session, instance=campus, unknown='exclude')
        campus.save()
        return campus

    @namespace.response(204, 'Campus year deleted')
    def delete(self, pk):
        campus = Campus.query.get_or_404(pk)
        return campus.delete(), 204


namespace.add_resource(Search, 'campus/search', endpoint='campus_search')
namespace.add_resource(CampusList, '/campuses', endpoint='campuses')
namespace.add_resource(CampusDetail, '/campus/<uuid:pk>', endpoint='campus')
