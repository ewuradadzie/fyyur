"""empty message

Revision ID: 5a1e181e1748
Revises: b5b1093f8579
Create Date: 2022-06-04 20:58:30.039476

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a1e181e1748'
down_revision = 'b5b1093f8579'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'artists', ['name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'artists', type_='unique')
    # ### end Alembic commands ###
