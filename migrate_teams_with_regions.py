#!/usr/bin/env python
"""
Smart migration using Kenya region-to-county mapping.
This understands that regions contain counties.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions.db import db
from app.models.team import Team
from app.models.county import County

# Kenya regions and their counties
KENYA_REGIONS = {
    'Central': ['Kiambu', 'Kirinyaga', 'Murang\'a', 'Nyandarua', 'Nyeri'],
    'Coast': ['Kilifi', 'Kwale', 'Lamu', 'Mombasa', 'Taita-Taveta', 'Tana River'],
    'Eastern': ['Embu', 'Isiolo', 'Kitui', 'Machakos', 'Makueni', 'Marsabit', 'Meru', 'Tharaka-Nithi'],
    'Nairobi': ['Nairobi'],
    'North Eastern': ['Garissa', 'Mandera', 'Wajir'],
    'Nyanza': ['Homa Bay', 'Kisii', 'Kisumu', 'Migori', 'Nyamira', 'Siaya'],
    'Rift Valley': [
        'Baringo', 'Bomet', 'Elgeyo-Marakwet', 'Kajiado', 'Kericho', 'Laikipia',
        'Nakuru', 'Nandi', 'Narok', 'Samburu', 'Trans-Nzoia', 'Turkana',
        'Uasin Gishu', 'West Pokot'
    ],
    'Western': ['Bungoma', 'Busia', 'Kakamega', 'Vihiga']
}

def migrate_teams_properly():
    """Migrate teams using proper region->county hierarchy"""
    
    app = create_app()
    
    with app.app_context():
        teams_without_county = Team.query.filter(Team.county_id.is_(None)).all()
        
        print(f"\n=== TEAM COUNTY MIGRATION (Region-Aware) ===")
        print(f"Found {len(teams_without_county)} teams without county_id\n")
        
        updated_count = 0
        failed_teams = []
        
        for team in teams_without_county:
            county = None
            match_info = ""
            
            # Strategy 1: If region field is a real region name, check if city is a county in that region
            if team.region and team.region in KENYA_REGIONS:
                print(f"\n[*] Team '{team.name}':")
                print(f"    Region: {team.region}")
                print(f"    City: {team.city}")
                
                counties_in_region = KENYA_REGIONS[team.region]
                print(f"    Counties in {team.region}: {counties_in_region}")
                
                # Try to match city to a county in this region
                if team.city and team.city in counties_in_region:
                    county = County.query.filter_by(name=team.city).first()
                    if county:
                        match_info = f"region '{team.region}' -> city '{team.city}' (county in region)"
            
            # Strategy 2: If region field is actually a county name, find its region and get county_id
            elif team.region:
                # Check which region contains this team.region as a county
                for region_name, counties_list in KENYA_REGIONS.items():
                    if team.region in counties_list:
                        county = County.query.filter_by(name=team.region).first()
                        if county:
                            match_info = f"region field '{team.region}' is a county in region '{region_name}'"
                        break
            
            if county:
                team.county_id = county.id
                print(f"    [OK] Matched: {match_info}")
                print(f"    [OK] Set county_id to {county.id}")
                updated_count += 1
            else:
                print(f"    [NO] Could not find county")
                failed_teams.append({
                    'name': team.name,
                    'region': team.region,
                    'city': team.city
                })
        
        # Commit all changes
        if updated_count > 0:
            try:
                db.session.commit()
                print(f"\n[OK] Successfully updated {updated_count} teams")
            except Exception as e:
                db.session.rollback()
                print(f"\n[NO] Error committing: {e}")
                return False
        
        if failed_teams:
            print(f"\n[!!] {len(failed_teams)} teams could not be auto-matched:")
            print("\n" + "="*70)
            for team in failed_teams:
                print(f"Team: {team['name']}")
                print(f"  Region: {team['region']}")
                print(f"  City: {team['city']}")
                print(f"  Action: Needs manual assignment to a county")
                print("-"*70)
            
            print("\nAvailable regions and their counties:")
            for region, counties in sorted(KENYA_REGIONS.items()):
                print(f"\n  {region}:")
                for county in counties:
                    print(f"    - {county}")
        
        print(f"\n=== MIGRATION COMPLETE ===\n")
        return True

if __name__ == '__main__':
    success = migrate_teams_properly()
    sys.exit(0 if success else 1)
