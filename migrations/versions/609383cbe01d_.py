"""empty message

Revision ID: 609383cbe01d
Revises: bd085567ac0d
Create Date: 2021-04-12 18:10:48.574331

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '609383cbe01d'
down_revision = 'bd085567ac0d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('invoice_ibfk_2', 'invoice', type_='foreignkey')
    op.drop_column('invoice', 'credit_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('invoice', sa.Column('credit_id', mysql.VARCHAR(length=100), nullable=True))
    op.create_foreign_key('invoice_ibfk_2', 'invoice', 'credit', ['credit_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###
