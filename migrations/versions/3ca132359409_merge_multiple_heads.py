"""merge multiple heads

Revision ID: 3ca132359409
Revises: bca476e43aaa, t1c2k3e4t5s6
Create Date: 2026-03-16 12:47:43.525606

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ca132359409'
down_revision = ('bca476e43aaa', 't1c2k3e4t5s6')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
