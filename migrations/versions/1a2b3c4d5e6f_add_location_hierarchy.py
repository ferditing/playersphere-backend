"""Add location hierarchy tables and location references to coaches and teams

Revision ID: 1a2b3c4d5e6f
Revises: fa4d6875a5ef
Create Date: 2026-02-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = 'fa4d6875a5ef'
branch_labels = None
depends_on = None


def upgrade():
    # Create Country table
    op.create_table(
        'countries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.Text(), nullable=False, unique=True),
        sa.Column('code', sa.String(2), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create Region table
    op.create_table(
        'regions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('country_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('code', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['country_id'], ['countries.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('country_id', 'name', name='uq_region_country_name')
    )

    # Create County table
    op.create_table(
        'counties',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('region_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('code', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('region_id', 'name', name='uq_county_region_name')
    )

    # Create Ward table
    op.create_table(
        'wards',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('county_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('code', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['county_id'], ['counties.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('county_id', 'name', name='uq_ward_county_name')
    )

    # Create indexes for faster lookups
    op.create_index(op.f('ix_regions_country_id'), 'regions', ['country_id'], unique=False)
    op.create_index(op.f('ix_counties_region_id'), 'counties', ['region_id'], unique=False)
    op.create_index(op.f('ix_wards_county_id'), 'wards', ['county_id'], unique=False)

    # Add county_id to coaches table
    with op.batch_alter_table('coaches', schema=None) as batch_op:
        batch_op.add_column(sa.Column('county_id', postgresql.UUID(as_uuid=True), nullable=True))
        batch_op.add_column(sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'))
        batch_op.add_column(sa.Column('must_change_password', sa.Boolean(), nullable=False, server_default='false'))
        batch_op.add_column(sa.Column('created_by_admin_id', postgresql.UUID(as_uuid=True), nullable=True))
        batch_op.create_foreign_key('fk_coaches_county_id', 'counties', ['county_id'], ['id'])
        batch_op.create_index(op.f('ix_coaches_county_id'), ['county_id'], unique=False)

    # Add county_id to teams table
    with op.batch_alter_table('teams', schema=None) as batch_op:
        batch_op.add_column(sa.Column('county_id', postgresql.UUID(as_uuid=True), nullable=True))
        batch_op.add_column(sa.Column('created_by_admin_id', postgresql.UUID(as_uuid=True), nullable=True))
        batch_op.create_foreign_key('fk_teams_county_id', 'counties', ['county_id'], ['id'])
        batch_op.create_index(op.f('ix_teams_county_id'), ['county_id'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_wards_county_id'), table_name='wards')
    op.drop_index(op.f('ix_counties_region_id'), table_name='counties')
    op.drop_index(op.f('ix_regions_country_id'), table_name='regions')
    op.drop_index(op.f('ix_teams_county_id'), table_name='teams')
    op.drop_index(op.f('ix_coaches_county_id'), table_name='coaches')

    # Revert coaches table
    with op.batch_alter_table('coaches', schema=None) as batch_op:
        batch_op.drop_constraint('fk_coaches_county_id', type_='foreignkey')
        batch_op.drop_column('created_by_admin_id')
        batch_op.drop_column('must_change_password')
        batch_op.drop_column('email_verified')
        batch_op.drop_column('county_id')

    # Revert teams table
    with op.batch_alter_table('teams', schema=None) as batch_op:
        batch_op.drop_constraint('fk_teams_county_id', type_='foreignkey')
        batch_op.drop_column('created_by_admin_id')
        batch_op.drop_column('county_id')

    # Drop location tables
    op.drop_table('wards')
    op.drop_table('counties')
    op.drop_table('regions')
    op.drop_table('countries')
