#!/usr/bin/env python
"""Test script to verify all imports work"""
import sys
sys.path.insert(0, '.')

try:
    print("Testing imports...")
    from app import create_app
    print("✓ create_app imported")
    
    app = create_app()
    print("✓ Flask app created")
    
    with app.app_context():
        from app.models import (
            Competition, CompetitionTeam, CompetitionGroup,
            KnockoutRound, CompetitionAdvancementRule, Match
        )
        print("✓ All Competition models imported")
        
        from app.services.competition_service import CompetitionService
        print("✓ CompetitionService imported")
        
        from app.services.scheduling_service import SchedulingService
        print("✓ SchedulingService imported")
        
        from app.services.advancement_service import AdvancementService
        print("✓ AdvancementService imported")
        
        from app.routes.competition_routes import competition_bp
        print("✓ competition_bp blueprint imported")
    
    print("\n✅ All imports successful! Ready for migration.")
    
except Exception as e:
    print(f"\n❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
