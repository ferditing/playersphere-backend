"""
Location Seeding Service

Seeds the database with country, region, county, and ward data.
Can be run once during initial migration or on demand.
"""

from app.extensions.db import db
from app.models import Country, Region, County, Ward
from app.services.location_seed_data import KENYA_DATA


def seed_locations():
    """
    Seeds the database with Kenya location hierarchy.
    Idempotent - will not create duplicates if already seeded.
    """
    try:
        # Check if Kenya already exists
        kenya = Country.query.filter_by(code='KE').first()
        
        if kenya:
            print("[OK] Kenya already exists in database. Skipping seeding.")
            return True
        
        # Create Kenya
        kenya = Country(
            name=KENYA_DATA['country']['name'],
            code=KENYA_DATA['country']['code']
        )
        db.session.add(kenya)
        db.session.flush()  # Flush to get Kenya ID
        
        print(f"[OK] Created Country: {kenya.name}")
        
        # Create Regions and Counties
        for region_name, counties in KENYA_DATA['regions'].items():
            region = Region(
                country_id=kenya.id,
                name=region_name,
                code=f'KE_{region_name.upper().replace(" ", "_")}'
            )
            db.session.add(region)
            db.session.flush()  # Flush to get region ID
            
            print(f"  [OK] Created Region: {region_name}")
            
            # Create Counties
            for county_name in counties:
                county = County(
                    region_id=region.id,
                    name=county_name,
                    code=f'KE_{county_name.upper().replace(" ", "_").replace("'", "")}'
                )
                db.session.add(county)
                db.session.flush()  # Flush to get county ID
                
                # Create Wards for counties with data
                
                
                print(f"    [OK] Created County: {county_name}")
        
        # Commit all changes
        db.session.commit()
        print("\n[OK] Location seeding completed successfully!")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f" Error during location seeding: {str(e)}")
        raise


def clear_locations():
    """
    Clears all location data from the database.
    WARNING: This will delete all countries, regions, counties, and wards.
    """
    try:
        Ward.query.delete()
        County.query.delete()
        Region.query.delete()
        Country.query.delete()
        db.session.commit()
        print("[OK] All location data cleared successfully!")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error clearing location data: {str(e)}")
        raise


def get_county_by_name(county_name: str):
    """Get a county by name"""
    return County.query.filter_by(name=county_name).first()


def get_region_by_name(region_name: str):
    """Get a region by name"""
    return Region.query.filter_by(name=region_name).first()


def get_all_regions():
    """Get all regions"""
    return Region.query.all()


def get_counties_by_region(region_id):
    """Get all counties in a region"""
    return County.query.filter_by(region_id=region_id).all()



