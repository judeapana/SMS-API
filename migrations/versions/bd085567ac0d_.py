"""empty message

Revision ID: bd085567ac0d
Revises: 35dcb682e6c3
Create Date: 2021-04-12 15:37:31.261101

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd085567ac0d'
down_revision = '35dcb682e6c3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transaction', sa.Column('status', sa.Numeric(precision=10, scale=2, asdecimal=False), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('transaction', 'status')
    # ### end Alembic commands ###
