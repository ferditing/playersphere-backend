"""merge multiple heads

Revision ID: 4003ba29c7be
Revises: abc123def456, b1e2c3d4f6a7
Create Date: 2026-01-22 21:52:56.148925

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4003ba29c7be'
down_revision = ('abc123def456', 'b1e2c3d4f6a7')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
