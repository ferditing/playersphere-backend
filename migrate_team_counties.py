#!/usr/bin/env python
"""
Migration script to populate county_id for existing teams based on their region.
Run this once to backfill the county_id field.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions.db import db
from app.models.team import Team
from app.models.county import County

def migrate_team_counties():
    """Populate county_id for all teams that have a region but no county_id"""
    
    app = create_app()
    
    with app.app_context():
        # Get all teams without county_id
        teams_without_county = Team.query.filter(Team.county_id.is_(None)).all()
        
        print(f"\n=== TEAM COUNTY MIGRATION ===")
        print(f"Found {len(teams_without_county)} teams without county_id\n")
        
        updated_count = 0
        failed_teams = []
        
        for team in teams_without_county:
            if not team.region:
                print(f"⚠️  Team '{team.name}' has no region - SKIPPING")
                continue
            
            # Find county by name matching the region
            county = County.query.filter_by(name=team.region).first()
            
            if county:
                team.county_id = county.id
                print(f"✓ Team '{team.name}': {team.region} → County ID: {county.id}")
                updated_count += 1
            else:
                print(f"✗ Team '{team.name}': Could not find county for region '{team.region}'")
                failed_teams.append((team.name, team.region))
        
        # Commit all changes
        if updated_count > 0:
            try:
                db.session.commit()
                print(f"\n✓ Successfully updated {updated_count} teams")
            except Exception as e:
                db.session.rollback()
                print(f"\n✗ Error committing changes: {e}")
                return False
        
        if failed_teams:
            print(f"\n⚠️  {len(failed_teams)} teams could not be matched:")
            for name, region in failed_teams:
                print(f"   - {name} (region: {region})")
            print("\nPlease check if these region names match any county names in the database.")
        
        print(f"\n=== MIGRATION COMPLETE ===\n")
        return True

if __name__ == '__main__':
    success = migrate_team_counties()
    sys.exit(0 if success else 1)
