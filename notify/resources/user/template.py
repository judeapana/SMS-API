from flask import request
from flask_jwt_extended import current_user
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus.reqparse import RequestParser

from notify import flask_filter, pagination, db
from notify.models import Template
from notify.resources.user import namespace
from notify.resources.utils import SearchParam, paginate_fields, search, base_fields
from notify.schema import TemplateSchema

mschema = TemplateSchema()

model = namespace.clone('Template', base_fields, {
    'title': fields.String(),
    'message': fields.String(),
})

parser = RequestParser(bundle_errors=True, trim=True)
parser.add_argument('title', required=True, type=str, location='json')
parser.add_argument('message', required=True, type=str, location='json')


class Search(Resource):

    @namespace.expect(search)
    def post(self):
        _search = flask_filter.search(current_user.templates, [request.json.get('filters')], TemplateSchema(many=True),
                                      order_by=request.json.get('order_by', 'created'))
        return pagination.paginate(_search, mschema, True,
                                   pagination_schema_hook=SearchParam(
                                       current_user.templates).paginate_fields_with_filter)


class TemplateList(Resource):

    def get(self):
        return pagination.paginate(current_user.templates, mschema, True, pagination_schema_hook=paginate_fields)

    @namespace.expect(model)
    @namespace.marshal_with(model, code=201)
    def post(self):
        template = Template()
        args = parser.parse_args(strict=True)
        mschema.load(data=args, session=db.session, instance=template, unknown='exclude')
        current_user.templates.append(template)
        current_user.save()
        return template


@namespace.param('pk', description='primary key')
class TemplateDetail(Resource):

    @namespace.marshal_with(model)
    def get(self, pk):
        template = current_user.templates.filter(Template.id == pk).first_or_404()
        return template

    @namespace.response(204, 'Template deleted')
    def delete(self, pk):
        template = current_user.templates.filter(Template.id == pk).first_or_404()
        return template.delete(), 204


namespace.add_resource(Search, '/templates/search', endpoint='user_template_search')
namespace.add_resource(TemplateList, '/template', endpoint='user_templates')
namespace.add_resource(TemplateDetail, '/template/<uuid:pk>', endpoint='user_template')
