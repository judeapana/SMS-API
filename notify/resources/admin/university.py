from flask import request
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus.reqparse import RequestParser

from notify import flask_filter, pagination, db, ErrorCodes
from notify.models import University
from notify.resources.admin import namespace
from notify.resources.utils import SearchParam, paginate_fields, search, base_fields
from notify.schema import UniversitySchema

mschema = UniversitySchema()

model = namespace.clone('Academic Year', base_fields, {
    'name': fields.String(),
})

parser = RequestParser(bundle_errors=True, trim=True)
parser.add_argument('name', required=True, type=str, location='json')


class Search(Resource):

    @namespace.expect(search)
    def post(self):
        _search = flask_filter.search(University, [request.json.get('filters')], UniversitySchema(many=True),
                                      order_by=request.json.get('order_by', 'created'))
        return pagination.paginate(_search, mschema, True,
                                   pagination_schema_hook=SearchParam(University).paginate_fields_with_filter, )


class UniversityList(Resource):
    method_decorators = []

    def get(self):
        rqp = RequestParser(trim=True)
        rqp.add_argument('all', location='args', type=bool)
        args = rqp.parse_args()
        if args.all:
            return mschema.dump(obj=University.query.all(), many=True)
        return pagination.paginate(University, mschema, True, pagination_schema_hook=paginate_fields)

    @namespace.expect(model)
    def post(self):
        errors = []
        university = University()
        args = parser.parse_args(strict=True)
        if University.query.filter(University.name == args.name).first():
            errors.append(ErrorCodes.UNIVERSITY_ALREADY_EXIST)
        if errors:
            return errors, 400
        mschema.load(data=args, session=db.session, instance=university, unknown='exclude')
        university.save()
        return {'message': 'University successfully added'}, 200


@namespace.param('pk', description='primary key')
class UniversityDetail(Resource):

    @namespace.marshal_with(model)
    def get(self, pk):
        university = University.query.get_or_404(pk)
        return university

    @namespace.expect(model)
    @namespace.marshal_with(model)
    def put(self, pk):
        errors = []
        university = University.query.get_or_404(pk)
        args = parser.parse_args()
        if University.query.filter(University.name == args.name, University.id != pk).first():
            errors.append(ErrorCodes.UNIVERSITY_ALREADY_EXIST)
        if errors:
            return errors, 400
        mschema.load(data=args, session=db.session, instance=university, unknown='exclude')
        university.save()
        return university

    @namespace.response(204, 'University deleted')
    def delete(self, pk):
        university = University.query.get_or_404(pk)
        return university.delete(), 204


namespace.add_resource(Search, '/university/search', endpoint='university_search')
namespace.add_resource(UniversityList, '/universities', endpoint='universities')
namespace.add_resource(UniversityDetail, '/university/<uuid:pk>', endpoint='university')
