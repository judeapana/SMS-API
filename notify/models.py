import datetime
from uuid import uuid4

import phonenumbers
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import EmailType, PhoneNumberType

from notify.ext import db
from notify.resources.constants import PER_SMS
from notify.utils import Record


def uuid_col():
    return str(uuid4())


class User(db.Model, Record):
    id = db.Column(db.String(100), primary_key=True, nullable=False, unique=True, default=uuid_col)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    email_address = db.Column(EmailType, nullable=False, unique=True)
    phone_number = db.Column(db.String(100), nullable=False, unique=True)
    role = db.Column(db.Enum('USER', 'ADMIN', 'SUPPORT'), nullable=False)
    account_type = db.Column(db.Enum('INDIVIDUAL', 'BUSINESS', 'OTHERS'), nullable=True)
    last_logged_in = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    active = db.Column(db.Boolean, nullable=False)
    campus_id = db.Column(db.String(100), db.ForeignKey('campus.id', ondelete='cascade'), nullable=True)
    niches = db.relationship('UserNiche', backref=db.backref('user'), cascade='all,delete,delete-orphan',
                             lazy='dynamic')
    credits = db.relationship('Credit', backref=db.backref('user'), cascade='all,delete,delete-orphan',
                              lazy='dynamic')
    invoices = db.relationship('Invoice', backref=db.backref('user'), cascade='all,delete,delete-orphan',
                               lazy='dynamic')
    templates = db.relationship('Template', backref=db.backref('user'), cascade='all,delete,delete-orphan',
                                lazy='dynamic')
    sent_msg = db.relationship('Message', backref=db.backref('user'), cascade='all,delete,delete-orphan',
                               lazy='dynamic', foreign_keys='Message.user_id')
    contact_list = db.relationship('ContactList', backref=db.backref('user'), cascade='all,delete,delete-orphan',
                                   lazy='dynamic')
    feedbacks = db.relationship('Feedback', backref=db.backref('user'), cascade='all,delete,delete-orphan',
                                lazy='dynamic')
    transactions = db.relationship('Transaction', backref=db.backref('user'), cascade='all,delete,delete-orphan',
                                   lazy='dynamic')

    @hybrid_property
    def parse_phone_number(self):
        hn = phonenumbers.parse(self.phone_number, 'GH')
        return phonenumbers.format_number(hn, phonenumbers.PhoneNumberFormat.E164).replace('+', '')


class University(db.Model, Record):
    id = db.Column(db.String(100), primary_key=True, nullable=False, unique=True, default=uuid_col)
    name = db.Column(db.String(100), nullable=False, unique=True)
    campuses = db.relationship('Campus', backref=db.backref('university'), cascade='all,delete,delete-orphan',
                               lazy='dynamic')


class Campus(db.Model, Record):
    id = db.Column(db.String(100), primary_key=True, nullable=False, unique=True, default=uuid_col)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(100), nullable=True)
    university_id = db.Column(db.String(100), db.ForeignKey('university.id', ondelete='cascade'), nullable=False)


class NicheAchieve(db.Model, Record):
    id = db.Column(db.String(100), primary_key=True, nullable=False, unique=True, default=uuid_col)
    interest = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    users_niche = db.relationship('UserNiche', backref=db.backref('niche_achieve'), cascade='all,delete,delete-orphan',
                                  lazy='dynamic')


class UserNiche(db.Model, Record):
    id = db.Column(db.String(100), primary_key=True, nullable=False, unique=True, default=uuid_col)
    user_id = db.Column(db.String(100), db.ForeignKey('user.id', ondelete='cascade'), nullable=False)
    niche_achieve_id = db.Column(db.String(100), db.ForeignKey('niche_achieve.id', ondelete='cascade'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)


class Credit(db.Model, Record):
    id = db.Column(db.String(100), primary_key=True, nullable=False, unique=True, default=uuid_col)
    user_id = db.Column(db.String(100), db.ForeignKey('user.id', ondelete='cascade'), nullable=False)
    form = db.Column(db.Enum('BONUS', 'MAIN'), nullable=False)
    unit = db.Column(db.Integer, nullable=False)


class Invoice(db.Model, Record):
    id = db.Column(db.String(100), primary_key=True, nullable=False, unique=True, default=uuid_col)
    user_id = db.Column(db.String(100), db.ForeignKey('user.id', ondelete='cascade'), nullable=True)
    amount = db.Column(db.Numeric(10, 2, asdecimal=False), nullable=False)
    payment_mode = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    note = db.Column(db.Text, nullable=False)
    transaction = db.relationship('Transaction', backref=db.backref('invoice'), cascade='all,delete,delete-orphan',
                                  uselist=False)

    @hybrid_property
    def credit_amt(self):
        return int(self.amount / PER_SMS)


class Transaction(db.Model, Record):
    id = db.Column(db.String(100), primary_key=True, nullable=False, unique=True, default=uuid_col)
    user_id = db.Column(db.String(100), db.ForeignKey('user.id', ondelete='cascade'), nullable=True)
    invoice_id = db.Column(db.String(100), db.ForeignKey('invoice.id', ondelete='cascade'), nullable=True, unique=True)
    txRef = db.Column(db.String(100), nullable=False)
    orderRef = db.Column(db.String(100), nullable=False)
    app_fee = db.Column(db.String(100), nullable=False)
    charged_amount = db.Column(db.Numeric(10, 2, asdecimal=False), nullable=False)
    currency = db.Column(db.String(100))
    amount = db.Column(db.Numeric(10, 2, asdecimal=False), nullable=False)
    status = db.Column(db.Numeric(10, 2, asdecimal=False), nullable=False)


class Template(db.Model, Record):
    id = db.Column(db.String(100), primary_key=True, nullable=False, unique=True, default=uuid_col)
    user_id = db.Column(db.String(100), db.ForeignKey('user.id', ondelete='cascade'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(100), nullable=False, info={'min': 10, 'max': 160})


class Message(db.Model, Record):
    """
        user_id is sender_id
    """
    id = db.Column(db.String(100), primary_key=True, nullable=False, unique=True, default=uuid_col)
    user_id = db.Column(db.String(100), db.ForeignKey('user.id', ondelete='cascade'), nullable=False)
    message = db.Column(db.Text, nullable=False, info={'min': 10, 'max': 160})
    option = db.Column(db.Enum('Flash Text', 'Text'), nullable=False)
    condition = db.Column(db.Enum('FAILED', 'SUCCESS', 'PENDING'), nullable=False)


class ContactList(db.Model, Record):
    id = db.Column(db.String(100), primary_key=True, nullable=False, unique=True, default=uuid_col)
    user_id = db.Column(db.String(100), db.ForeignKey('user.id', ondelete='cascade'), nullable=False)
    contact_name = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(PhoneNumberType(region='GH'), nullable=False)
    email_address = db.Column(db.String(100), nullable=True)
    active = db.Column(db.Boolean, default=True)


class Feedback(db.Model, Record):
    id = db.Column(db.String(100), primary_key=True, nullable=False, unique=True, default=uuid_col)
    user_id = db.Column(db.String(100), db.ForeignKey('user.id', ondelete='cascade'), nullable=True)
    title = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    message = db.Column(db.Text, nullable=True)
