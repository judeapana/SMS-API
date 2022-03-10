"""empty message

Revision ID: cda4228d748a
Revises: 6725f358c99b
Create Date: 2021-04-10 21:40:27.450385

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cda4228d748a'
down_revision = '6725f358c99b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('campus', sa.Column('description', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('campus', 'description')
    # ### end Alembic commands ###