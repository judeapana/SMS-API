"""empty message

Revision ID: 35dcb682e6c3
Revises: f81d394057be
Create Date: 2021-04-12 15:23:33.537274

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '35dcb682e6c3'
down_revision = 'f81d394057be'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transaction', sa.Column('invoice_id', sa.String(length=100), nullable=True))
    op.add_column('transaction', sa.Column('user_id', sa.String(length=100), nullable=True))
    op.create_foreign_key(None, 'transaction', 'invoice', ['invoice_id'], ['id'], ondelete='cascade')
    op.create_foreign_key(None, 'transaction', 'user', ['user_id'], ['id'], ondelete='cascade')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'transaction', type_='foreignkey')
    op.drop_constraint(None, 'transaction', type_='foreignkey')
    op.drop_column('transaction', 'user_id')
    op.drop_column('transaction', 'invoice_id')
    # ### end Alembic commands ###