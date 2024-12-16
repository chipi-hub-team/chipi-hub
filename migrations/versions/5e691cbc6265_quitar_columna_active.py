"""Quitar columna active

Revision ID: 5e691cbc6265
Revises: e1a48b0fba37
Create Date: 2024-12-15 01:07:30.443842

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '5e691cbc6265'
down_revision = 'e1a48b0fba37'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('active')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('active', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))

    # ### end Alembic commands ###