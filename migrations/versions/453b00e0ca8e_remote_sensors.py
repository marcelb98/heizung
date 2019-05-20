"""remote sensors

Revision ID: 453b00e0ca8e
Revises: 3cf7480569d1
Create Date: 2019-05-20 19:37:40.689172

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '453b00e0ca8e'
down_revision = '3cf7480569d1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('remotesensor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('remotesensor')
