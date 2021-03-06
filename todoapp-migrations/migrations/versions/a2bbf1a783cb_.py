"""empty message

Revision ID: a2bbf1a783cb
Revises: 99a037ee0037
Create Date: 2020-04-25 17:39:22.135133

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2bbf1a783cb'
down_revision = '99a037ee0037'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('todos_list_id_fkey', 'todos', type_='foreignkey')
    op.create_foreign_key(None, 'todos', 'todolists', ['list_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'todos', type_='foreignkey')
    op.create_foreign_key('todos_list_id_fkey', 'todos', 'todolists', ['list_id'], ['id'])
    # ### end Alembic commands ###
