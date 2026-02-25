"""
Seed script for constituencies and wards
Run from Flask CLI: flask seed-constituencies-wards
"""
import click
from flask.cli import with_appcontext
from app.extensions.db import db
from app.models import County, Constituency, Ward
from app.services.seed_constituencies_wards import KENYA_CONSTITUENCIES_WARDS


@click.command('seed-constituencies-wards')
@with_appcontext
def seed_constituencies_wards():
    """Seed constituencies and wards from Kenya locations data"""
    
    try:
        total_constituencies = 0
        total_wards = 0
        
        for county_name, constituencies in KENYA_CONSTITUENCIES_WARDS.items():
            # Find the county
            county = County.query.filter_by(name=county_name).first()
            
            if not county:
                click.echo(f"[!] County '{county_name}' not found in database. Skipping...")
                continue
            
            click.echo(f"\n[*] Processing {county_name}...")
            
            for constituency_name, wards_list in constituencies.items():
                # Check if constituency already exists
                constituency = Constituency.query.filter_by(
                    name=constituency_name,
                    county_id=county.id
                ).first()
                
                if not constituency:
                    constituency = Constituency(
                        name=constituency_name,
                        county_id=county.id
                    )
                    db.session.add(constituency)
                    db.session.flush()
                    total_constituencies += 1
                    click.echo(f"  [+] Created constituency: {constituency_name}")
                
                # Add wards
                for ward_name in wards_list:
                    ward = Ward.query.filter_by(
                        name=ward_name,
                        constituency_id=constituency.id
                    ).first()
                    
                    if not ward:
                        ward = Ward(
                            name=ward_name,
                            county_id=county.id,
                            constituency_id=constituency.id
                        )
                        db.session.add(ward)
                        total_wards += 1
        
        # Commit all changes
        db.session.commit()
        click.echo(f"\n[OK] Seeding complete!")
        click.echo(f"   * Constituencies created: {total_constituencies}")
        click.echo(f"   * Wards created: {total_wards}")
        
    except Exception as e:
        db.session.rollback()
        click.echo(f"\nError seeding data: {str(e)}")
        raise


def register_seed_command(app):
    """Register the seed command with the Flask app"""
    app.cli.add_command(seed_constituencies_wards)
