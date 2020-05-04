"""empty message

Revision ID: 404020731e1a
Revises: 
Create Date: 2020-04-15 17:02:12.033941

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '404020731e1a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('todos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('todos')
    # ### end Alembic commands ###
