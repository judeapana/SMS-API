from marshmallow import fields

from notify import ma
from notify.models import University, ContactList, Feedback, Message, Template, Invoice, UserNiche, Credit, \
    NicheAchieve, Campus, User, Transaction


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_fk = True
        exclude = ('password',)

    parse_phone_number = fields.Function(lambda x: x.parse_phone_number)
    # campus = fields.Nested('CampusSchema')


class UniversitySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = University
        load_instance = True
        include_fk = True

    # campuses = fields.Nested('CampusSchema', many=True)


class CampusSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Campus
        load_instance = True
        include_fk = True

    university = fields.Nested(UniversitySchema, only=('name', 'id'))


class NicheAchieveSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = NicheAchieve
        load_instance = True
        include_fk = True

    # users_niche = fields.Nested('UserNicheSchema', many=True)


class UserNicheSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserNiche
        load_instance = True
        include_fk = True

    user = fields.Nested(UserSchema)
    niche_achieve = fields.Nested(NicheAchieveSchema, many=True)


class CreditSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Credit
        load_instance = True
        include_fk = True


class InvoiceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Invoice
        load_instance = True
        include_fk = True

    transaction = fields.Nested('TransactionSchema')
    # user = fields.Nested(UserSchema)


class TemplateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Template
        load_instance = True
        include_fk = True

    # user = fields.Nested(UserSchema)


class MessageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Message
        load_instance = True
        include_fk = True

    # user = fields.Nested(UserSchema)
    # send_to = fields.Nested(UserSchema)


class TransactionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Transaction
        load_instance = True
        include_fk = True


class ContactListSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ContactList
        load_instance = True
        include_fk = True

    user = fields.Nested(UserSchema)


class FeedbackSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Feedback
        load_instance = True
        include_fk = True
