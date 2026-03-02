"""Create admin table

Revision ID: a1b2c3d4e5f6
Revises: z9z9z9z9z9z9
Create Date: 2026-02-27 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'z9z9z9z9z9z9'
branch_labels = None
depends_on = None


def upgrade():
    # Create admins table
    op.create_table(
        'admins',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('full_name', sa.Text(), nullable=False),
        sa.Column('email', sa.Text(), nullable=False, unique=True),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('role', sa.Text(), nullable=False),
        sa.Column('county_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['county_id'], ['counties.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("role IN ('super_admin', 'county_admin', 'national_admin')"),
    )
    
    # Create index on email for faster lookups
    op.create_index(op.f('ix_admins_email'), 'admins', ['email'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_admins_email'), table_name='admins')
    op.drop_table('admins')
