"""merge multiple heads

Revision ID: bca476e43aaa
Revises: a19d02e15f2a, add_paused_to_matchstatus_enum
Create Date: 2026-03-15 16:23:35.984520

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bca476e43aaa'
down_revision = ('a19d02e15f2a', 'add_paused_to_matchstatus_enum')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
