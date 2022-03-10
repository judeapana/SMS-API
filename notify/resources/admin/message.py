import requests
from flask import request, current_app
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus.reqparse import RequestParser

from notify import flask_filter, pagination
from notify.models import Message, User
from notify.resources.admin import namespace
from notify.resources.utils import SearchParam, paginate_fields, search, base_fields
from notify.schema import MessageSchema
from notify.sms.SMS import SMS

mschema = MessageSchema()

model = namespace.clone('Message', base_fields, {
    'user_id': fields.String(),
    "message": fields.String(),
    "condition": fields.String(),
})

parser = RequestParser(bundle_errors=True, trim=True)
parser.add_argument('users', required=True, type=list, location='json')
parser.add_argument('message', required=True, type=str, location='json')
parser.add_argument('option', required=True, choices=['Flash Text', 'Text'], type=str, location='json')


class Search(Resource):

    @namespace.expect(search)
    def post(self):
        _search = flask_filter.search(Message, [request.json.get('filters')], MessageSchema(many=True),
                                      order_by=request.json.get('order_by', 'created'))
        return pagination.paginate(_search, mschema, True,
                                   pagination_schema_hook=SearchParam(Message).paginate_fields_with_filter)


class MessageList(Resource):

    def get(self):
        return pagination.paginate(Message, mschema, True, pagination_schema_hook=paginate_fields)

    @namespace.expect(model)
    def post(self):
        args = parser.parse_args(strict=True)
        messages = []
        for user_id in args.users:
            user = User.query.get(user_id)
            sms = SMS(args.option, args.message, current_app.config['TEXT_NAME'], [user.parse_phone_number])
            if sms.send():
                message = Message(user_id=user_id, message=args.message, option=args.option, condition='SUCCESS')
                messages.append(message)
                message.save()
            else:
                message = Message(user_id=user_id, message=args.message, option=args.option, condition='FAILED')
                messages.append(message)
                message.save()
        return mschema.dump(obj=messages, many=True)


@namespace.param('pk', description='primary key')
class MessageDetail(Resource):

    @namespace.marshal_with(model)
    def get(self, pk):
        message = Message.query.get_or_404(pk)
        return message

    @namespace.response(204, 'Message deleted')
    def delete(self, pk):
        message = Message.query.get_or_404(pk)
        return message.delete(), 204


class TextCus(Resource):
    def get(self):
        rq = requests.post('https://sms.textcus.com/api/balance', params={'apikey': current_app.config['SMS_API']})
        return rq.json()


namespace.add_resource(Search, '/messages/search', endpoint='message_search')
namespace.add_resource(Search, '/text-cus/balance', endpoint='balance')
namespace.add_resource(MessageList, '/messages', endpoint='messages')
namespace.add_resource(MessageDetail, '/messages/<uuid:pk>', endpoint='message')
