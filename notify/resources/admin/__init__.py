from flask_restplus import Namespace

from notify.utils import role_required

namespace = Namespace('Administration', 'Administrator ', decorators=[])
from . import campus, contact_list, credit, feedback, invoice, message, niche_achieve, template, university, user
