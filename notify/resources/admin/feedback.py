from flask import request
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus.reqparse import RequestParser

from notify import flask_filter, pagination, db
from notify.models import Feedback
from notify.resources.admin import namespace
from notify.resources.utils import SearchParam, paginate_fields, search, base_fields
from notify.schema import FeedbackSchema

mschema = FeedbackSchema()

model = namespace.clone('Feedback', base_fields, {
    'user_id': fields.String(),
    'title': fields.String(),
    'rating': fields.String(),
    'message': fields.Integer(),
})

parser = RequestParser(bundle_errors=True, trim=True)
parser.add_argument('user_id', required=True, type=str, location='json')
parser.add_argument('title', required=True, type=str, location='json')
parser.add_argument('rating', required=True, type=str, location='json')
parser.add_argument('message', required=True, type=str, location='json')


class Search(Resource):

    @namespace.expect(search)
    def post(self):
        _search = flask_filter.search(Feedback, [request.json.get('filters')], FeedbackSchema(many=True),
                                      order_by=request.json.get('order_by', 'created'))
        return pagination.paginate(_search, mschema, True,
                                   pagination_schema_hook=SearchParam(Feedback).paginate_fields_with_filter)


class FeedbackList(Resource):
    method_decorators = []

    def get(self):
        return pagination.paginate(Feedback, mschema, True, pagination_schema_hook=paginate_fields)

    @namespace.expect(model)
    @namespace.marshal_with(model, code=201)
    def post(self):
        feedback = Feedback()
        args = parser.parse_args(strict=True)
        mschema.load(data=args, session=db.session, instance=feedback, unknown='exclude')
        feedback.save()
        return feedback


@namespace.param('pk', description='primary key')
class FeedbackDetail(Resource):

    @namespace.marshal_with(model)
    def get(self, pk):
        feedback = Feedback.query.get_or_404(pk)
        return feedback

    @namespace.expect(model)
    @namespace.marshal_with(model)
    def put(self, pk):
        feedback = Feedback.query.get_or_404(pk)
        args = parser.parse_args(strict=True)
        mschema.load(data=args, session=db.session, instance=feedback, unknown='exclude')
        feedback.save()
        return feedback

    @namespace.response(204, 'feedback deleted')
    def delete(self, pk):
        feedback = Feedback.query.get_or_404(pk)
        return feedback.delete(), 204


namespace.add_resource(Search, '/feedback/search', endpoint='feedback_search')
namespace.add_resource(FeedbackList, '/feedbacks', endpoint='feedbacks')
namespace.add_resource(FeedbackDetail, '/feedback/<uuid:pk>', endpoint='feedback')
