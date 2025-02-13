"""empty message

Revision ID: 97cadb036068
Revises: 35c1cd36183f
Create Date: 2024-12-09 19:46:12.764259

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '97cadb036068'
down_revision = '35c1cd36183f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('state',
    sa.Column('state_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('state_name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('state_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('state')
    # ### end Alembic commands ###
