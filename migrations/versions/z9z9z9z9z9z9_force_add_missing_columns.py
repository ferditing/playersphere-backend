"""Force add missing columns to coaches and teams tables

Revision ID: z9z9z9z9z9z9
Revises: c9e3aa20359f
Create Date: 2026-02-27 08:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'z9z9z9z9z9z9'
down_revision = 'c9e3aa20359f'
branch_labels = None
depends_on = None


def upgrade():
    # Check and add county_id to coaches if it doesn't exist
    with op.batch_alter_table('coaches', schema=None) as batch_op:
        batch_op.add_column(sa.Column('county_id', postgresql.UUID(as_uuid=True), nullable=True))
        batch_op.add_column(sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'))
        batch_op.add_column(sa.Column('must_change_password', sa.Boolean(), nullable=False, server_default='false'))
        batch_op.add_column(sa.Column('created_by_admin_id', postgresql.UUID(as_uuid=True), nullable=True))
        batch_op.create_index(op.f('ix_coaches_county_id'), ['county_id'], unique=False)

    # Check and add county_id to teams if it doesn't exist
    with op.batch_alter_table('teams', schema=None) as batch_op:
        batch_op.add_column(sa.Column('county_id', postgresql.UUID(as_uuid=True), nullable=True))
        batch_op.add_column(sa.Column('created_by_admin_id', postgresql.UUID(as_uuid=True), nullable=True))
        batch_op.create_index(op.f('ix_teams_county_id'), ['county_id'], unique=False)


def downgrade():
    with op.batch_alter_table('teams', schema=None) as batch_op:
        batch_op.drop_index(op.f('ix_teams_county_id'))
        batch_op.drop_column('created_by_admin_id')
        batch_op.drop_column('county_id')

    with op.batch_alter_table('coaches', schema=None) as batch_op:
        batch_op.drop_index(op.f('ix_coaches_county_id'))
        batch_op.drop_column('created_by_admin_id')
        batch_op.drop_column('must_change_password')
        batch_op.drop_column('email_verified')
        batch_op.drop_column('county_id')
