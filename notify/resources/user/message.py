from flask import request
from flask_jwt_extended import current_user
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus.reqparse import RequestParser

from notify import flask_filter, pagination, db
from notify.models import Message, UserNiche, Credit
from notify.resources.constants import PER_SMS_LENGTH
from notify.resources.user import namespace
from notify.resources.utils import SearchParam, paginate_fields, search, base_fields
from notify.schema import MessageSchema, UserNicheSchema

mschema = MessageSchema()

model = namespace.clone('Message', base_fields, {
    "message": fields.String(),
    "condition": fields.String(),
})

parser = RequestParser(bundle_errors=True, trim=True)
parser.add_argument('message', required=True, type=float, location='json')
parser.add_argument('condition', required=True, type=str, location='json')


class Search(Resource):

    @namespace.expect(search)
    def post(self):
        _search = flask_filter.search(current_user.sent_msg, [request.json.get('filters')], MessageSchema(many=True),
                                      order_by=request.json.get('order_by', 'created'))
        return pagination.paginate(_search, mschema, True,
                                   pagination_schema_hook=SearchParam(
                                       current_user.sent_msg).paginate_fields_with_filter)


class MessageList(Resource):

    def get(self):
        return pagination.paginate(current_user.sent_msg, mschema, True, pagination_schema_hook=paginate_fields)

    @namespace.expect(model)
    @namespace.marshal_with(model, code=201)
    def post(self):
        message = Message()
        args = parser.parse_args(strict=True)
        mschema.load(data=args, session=db.session, instance=message, unknown='exclude')
        bonus = current_user.credits.filter(Credit.form == 'BONUS').first()
        main = current_user.credits.filter(Credit.form == 'MAIN').first()
        sms_len = int(len(args.message) / PER_SMS_LENGTH)
        if bonus > 0:
            bonus -= sms_len
            bonus.save()
        elif main > 0:
            main -= sms_len
            bonus.save()
        else:
            return 'Insufficient credits', 400
        current_user.sent_msg.append(message)
        current_user.save()
        return message


@namespace.param('pk', description='primary key')
class MessageDetail(Resource):

    @namespace.marshal_with(model)
    def get(self, pk):
        message = current_user.sent_msg.filter(Message.id == pk).first_or_404()
        return message

    @namespace.response(204, 'Message deleted')
    def delete(self, pk):
        message = current_user.sent_msg.filter(Message.id == pk).first_or_404()
        return message.delete(), 204


class CustomerNiche(Resource):
    def get(self):
        users = UserNiche.query.filter(UserNiche.niche_achieve.in_(current_user.niches.all())).all()
        schema = UserNicheSchema()
        return schema.dumps(obj=users)


namespace.add_resource(Search, '/msg/search', endpoint='user_message_search')
namespace.add_resource(MessageList, '/msgs', endpoint='user_messages')
namespace.add_resource(MessageDetail, '/msg/<uuid:pk>', endpoint='user_message')
