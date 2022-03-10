from flask_restplus import Namespace

from notify.utils import role_required

namespace = Namespace('User Functionality', 'user functionality', decorators=[role_required(['USER'])])

from . import buy, contact_list, credit, feedback, invoice, message, profile, template, transactions

