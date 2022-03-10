from flask import request
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus.reqparse import RequestParser

from notify import flask_filter, pagination, db
from notify.models import Template
from notify.resources.admin import namespace
from notify.resources.utils import SearchParam, paginate_fields, search, base_fields
from notify.schema import TemplateSchema

mschema = TemplateSchema()

model = namespace.clone('Template', base_fields, {
    'user_id': fields.String(),
    'title': fields.String(),
    'message': fields.String(),
})

parser = RequestParser(bundle_errors=True, trim=True)
parser.add_argument('user_id', required=True, type=str, location='json')
parser.add_argument('title', required=True, type=str, location='json')
parser.add_argument('message', required=True, type=str, location='json')


class Search(Resource):

    @namespace.expect(search)
    def post(self):
        _search = flask_filter.search(Template, [request.json.get('filters')], TemplateSchema(many=True),
                                      order_by=request.json.get('order_by', 'created'))
        return pagination.paginate(_search, mschema, True,
                                   pagination_schema_hook=SearchParam(Template).paginate_fields_with_filter)


class TemplateList(Resource):

    def get(self):
        return pagination.paginate(Template, mschema, True, pagination_schema_hook=paginate_fields)

    @namespace.expect(model)
    # @namespace.marshal_with(model, code=201)
    def post(self):
        template = Template()
        args = parser.parse_args(strict=True)
        mschema.load(data=args, session=db.session, instance=template, unknown='exclude')
        template.save()
        return template


@namespace.param('pk', description='primary key')
class TemplateDetail(Resource):

    @namespace.marshal_with(model)
    def get(self, pk):
        template = Template.query.get_or_404(pk)
        return template

    @namespace.expect(model)
    # @namespace.marshal_with(model)
    def put(self, pk):
        template = Template.query.get_or_404(pk)
        args = parser.parse_args(strict=True)
        mschema.load(data=args, session=db.session, instance=template, unknown='exclude')
        template.save()
        return template

    @namespace.response(204, 'Template deleted')
    def delete(self, pk):
        template = Template.query.get_or_404(pk)
        return template.delete(), 204


namespace.add_resource(Search, '/templates/search', endpoint='template_search')
namespace.add_resource(TemplateList, '/templates', endpoint='templates')
namespace.add_resource(TemplateDetail, '/template/<uuid:pk>', endpoint='template')
