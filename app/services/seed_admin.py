"""
Admin Seeding Service

Seeds the database with initial super admin user.
Run once during setup or on demand.
"""

import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
from app.extensions.db import db
from app.models import Admin


@click.command('seed-admin')
@click.option('--email', default=None, help='Admin email address')
@click.option('--password', default=None, help='Admin password')
@click.option('--name', default=None, help='Admin full name')
@with_appcontext
def seed_admin(email: str, password: str, name: str):
    """Create initial super admin user"""
    
    # Use defaults if not provided
    if not email:
        email = 'tingishaferdinand@gmail.com'
    if not password:
        password = 'Admin123!'
    if not name:
        name = 'System Administrator'
    
    try:
        # Check if admin already exists
        existing_admin = Admin.query.filter_by(email=email).first()
        if existing_admin:
            click.echo(f"[!] Admin with email '{email}' already exists. Skipping...")
            return
        
        # Create super admin
        admin = Admin(
            full_name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role='super_admin',
            county_id=None
        )
        
        db.session.add(admin)
        db.session.commit()
        
        click.echo(f"[+] Super admin created successfully!")
        click.echo(f"    Email: {email}")
        click.echo(f"    Name: {name}")
        click.echo(f"    Role: super_admin")
        click.echo(f"\n    Use these credentials to login and create county/national admins")
        
    except Exception as e:
        db.session.rollback()
        click.echo(f"[ERROR] Failed to create admin: {str(e)}")
        raise


def register_seed_admin_command(app):
    """Register the seed admin command with the Flask app"""
    app.cli.add_command(seed_admin)
# AdminPassword123!