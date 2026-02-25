"""Merge migration branches

Revision ID: e0b1f086b50d
Revises: 1a2b3c4d5e6f, dad9f91ef053
Create Date: 2026-02-24 19:55:27.069985

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e0b1f086b50d'
down_revision = ('1a2b3c4d5e6f', 'dad9f91ef053')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
