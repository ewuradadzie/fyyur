"""empty message

Revision ID: acfea1a87840
Revises: 43197f919af3
Create Date: 2022-06-04 22:51:57.913443

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'acfea1a87840'
down_revision = '43197f919af3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('shows', 'name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('name', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
