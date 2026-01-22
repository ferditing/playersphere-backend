"""update eventtype enum

Revision ID: abc123def456
Revises: fa4d6875a5ef
Create Date: 2026-01-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'abc123def456'
down_revision = 'fa4d6875a5ef'
branch_labels = None
depends_on = None


def upgrade():
    # Add penalty_goal to the eventtype enum
    op.execute("ALTER TYPE eventtype ADD VALUE 'penalty_goal'")


def downgrade():
    # Note: PostgreSQL doesn't support removing enum values easily
    # This would require recreating the enum without penalty_goal
    # For now, we'll leave it as is since downgrades are rare
    pass