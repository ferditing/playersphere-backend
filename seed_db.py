#!/usr/bin/env python
"""
Standalone script to seed the database.
Works in both local and production environments.
Run: python seed_db.py
"""
import sys
import os

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.services.location_service import seed_locations
from app.services.seed_command import seed_constituencies_wards


def main():
    """Run seeding operations"""
    try:
        print("Initializing Flask app...")
        app = create_app()
        
        with app.app_context():
            print("\n[*] Starting location seeding...")
            seed_locations()
            
            print("\n[*] Starting constituencies and wards seeding...")
            seed_constituencies_wards()
            
            print("\n[OK] All seeding completed successfully!")
            
    except Exception as e:
        print(f"\nError during seeding: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
