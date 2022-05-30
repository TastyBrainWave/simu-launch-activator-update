"""experience

Revision ID: 3ca28444a49e
Revises: 
Create Date: 2022-05-26 19:00:18.472957

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ca28444a49e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('items', sa.Column('experience_name', sa.String(), nullable=True))


def downgrade():
    pass
