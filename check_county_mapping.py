#!/usr/bin/env python
"""
Helper script to check which regions can be matched to counties
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions.db import db
from app.models.team import Team
from app.models.county import County

def check_county_mapping():
    """Show what regions exist and which can be matched to counties"""
    
    app = create_app()
    
    with app.app_context():
        # Get all unique regions from teams without county_id
        teams_without_county = Team.query.filter(Team.county_id.is_(None)).all()
        regions = set(t.region for t in teams_without_county if t.region)
        
        # Get all counties
        all_counties = County.query.all()
        county_names = {c.name for c in all_counties}
        
        print(f"\n=== COUNTY MAPPING REPORT ===\n")
        print(f"Teams without county_id: {len(teams_without_county)}")
        print(f"Unique regions used: {len(regions)}")
        print(f"Total counties in database: {len(all_counties)}\n")
        
        print("REGIONS → COUNTY MATCHES:")
        print("-" * 60)
        
        matched = 0
        unmatched = []
        
        for region in sorted(regions):
            county = County.query.filter_by(name=region).first()
            if county:
                teams_with_region = len([t for t in teams_without_county if t.region == region])
                print(f"✓ {region:20} → {str(county.id):36}  ({teams_with_region} teams)")
                matched += 1
            else:
                teams_with_region = len([t for t in teams_without_county if t.region == region])
                print(f"✗ {region:20} → NOT FOUND  ({teams_with_region} teams)")
                unmatched.append(region)
        
        print("-" * 60)
        print(f"\nMatched: {matched}/{len(regions)}")
        
        if unmatched:
            print(f"\nUNMATCHED REGIONS ({len(unmatched)}):")
            print("These region names don't match any county name in the database:")
            for region in sorted(unmatched):
                print(f"  - {region}")
            print("\nAvailable counties in database:")
            for county in sorted(all_counties, key=lambda c: c.name):
                print(f"  - {county.name}")
        
        print(f"\n=== END REPORT ===\n")

if __name__ == '__main__':
    check_county_mapping()
