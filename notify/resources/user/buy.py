import requests
from flask_restplus import Resource
from flask_restplus.reqparse import RequestParser

from notify import ErrorCodes
from notify.resources.constants import PER_SMS

parser = RequestParser(trim=True, bundle_errors=True)
parser.add_argument('phone_number', required=True, type=str, location='json')
parser.add_argument('network', required=True, choices=['MTN', 'VODAFONE', 'TIGO'], type=str, location='json')
parser.add_argument('email_address', required=True, type=str, location='json')
parser.add_argument('amount', required=True, type=float, location='json')
from notify.resources.user import namespace


class Buy(Resource):
    """
    post will make the request and retrieve the recaptcha url and
    put will send the otp and the watcher will watch for successful and failed transactions
    """

    def post(self):
        args = parser.parse_args(strict=True)
        payload = {
            "amount": args.amount,
            "email": args.email_address,
            "phonenumber": args.phone_number,
            "network": args.network,
            # "redirect_url": url_for(''),
            "IP": "127.0.0.1"
        }

        return

    def put(self):
        otp = RequestParser(trim=True)
        otp.add_argument('url', type=str, required=True, )
        otp.add_argument('solution', type=str, required=True)
        args = otp.parse_args(strict=True)
        req = requests.post(args.url + '?solution=' + args.solution)
        return req.content, 200


class CheckCredits(Resource):
    def post(self):
        args = parser.parse_args()
        if args.amount >= 1:
            return int(args.amount / PER_SMS)
        else:
            return ErrorCodes.INVALID_AMOUNT, 400


namespace.add_resource(CheckCredits, '/cal-credit', endpoint='check_credit')
namespace.add_resource(Buy, '/buy', endpoint='buy')
