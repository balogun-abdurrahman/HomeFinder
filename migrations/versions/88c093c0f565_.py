"""empty message

Revision ID: 88c093c0f565
Revises: 97cadb036068
Create Date: 2024-12-09 21:00:43.889636

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '88c093c0f565'
down_revision = '97cadb036068'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('property_listing', schema=None) as batch_op:
        batch_op.add_column(sa.Column('property_type_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'property_type', ['property_type_id'], ['property_id'])
        batch_op.drop_column('property_type')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('property_listing', schema=None) as batch_op:
        batch_op.add_column(sa.Column('property_type', mysql.ENUM('0', '1'), server_default=sa.text("'0'"), nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('property_type_id')

    # ### end Alembic commands ###
