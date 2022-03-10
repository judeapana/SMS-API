from flask_jwt_extended import current_user
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus.reqparse import RequestParser

from notify import pagination, db
from notify.models import Feedback
from notify.resources.user import namespace
from notify.resources.utils import paginate_fields, base_fields
from notify.schema import FeedbackSchema

mschema = FeedbackSchema()

model = namespace.clone('Feedback', base_fields, {
    'title': fields.String(),
    'rating': fields.String(),
    'message': fields.Integer(),
})

parser = RequestParser(bundle_errors=True, trim=True)
parser.add_argument('title', required=True, type=str, location='json')
parser.add_argument('rating', required=True, type=str, location='json')
parser.add_argument('message', required=True, type=str, location='json')


class FeedbackList(Resource):
    method_decorators = []

    def get(self):
        return pagination.paginate(current_user.feedbacks, mschema, True, pagination_schema_hook=paginate_fields)

    @namespace.expect(model)
    @namespace.marshal_with(model, code=201)
    def post(self):
        feedback = Feedback()
        args = parser.parse_args(strict=True)
        mschema.load(data=args, session=db.session, instance=feedback, unknown='exclude')
        current_user.feedbacks.append(feedback)
        current_user.save()
        return feedback


@namespace.param('pk', description='primary key')
class FeedbackDetail(Resource):

    @namespace.marshal_with(model)
    def get(self, pk):
        feedback = current_user.feedbacks.filter_by(Feedback.id == pk).first_or_404()
        return feedback

    @namespace.response(204, 'feedback deleted')
    def delete(self, pk):
        feedback = current_user.feedbacks.filter_by(Feedback.id == pk).first_or_404()
        return feedback.delete(), 204


namespace.add_resource(FeedbackList, '/feedbacks', endpoint='user_feedbacks')
namespace.add_resource(FeedbackDetail, '/feedback/<uuid:pk>', endpoint='user_feedback')
