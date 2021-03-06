"""empty message

Revision ID: 19e3aba9b1ef
Revises: 609383cbe01d
Create Date: 2021-04-22 02:36:19.050109

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '19e3aba9b1ef'
down_revision = '609383cbe01d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('message', sa.Column('option', sa.Enum('Flash Text', 'Text'), nullable=False))
    op.drop_constraint('message_ibfk_1', 'message', type_='foreignkey')
    op.drop_column('message', 'send_to_id')
    op.create_unique_constraint(None, 'transaction', ['invoice_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'transaction', type_='unique')
    op.add_column('message', sa.Column('send_to_id', mysql.VARCHAR(length=100), nullable=True))
    op.create_foreign_key('message_ibfk_1', 'message', 'user', ['send_to_id'], ['id'], ondelete='CASCADE')
    op.drop_column('message', 'option')
    # ### end Alembic commands ###
