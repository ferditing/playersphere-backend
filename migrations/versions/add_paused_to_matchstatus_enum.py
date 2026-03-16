"""
Add 'paused' to matchstatus enum
"""

from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = 'add_paused_to_matchstatus_enum'
down_revision = 'cc8083077915'
branch_labels = None
depends_on = None

def upgrade():
    # Add the new value to the matchstatus enum
    op.execute("ALTER TYPE matchstatus ADD VALUE 'paused'")

def downgrade():
    # Downgrade is not supported for enum modifications
    pass