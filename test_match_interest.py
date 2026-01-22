# test_match_interest.py
import uuid
from app import create_app
from app.extensions.db import db
from app.models.coach import Coach
from app.models.team import Team
from app.services.match_interest_service import create_match_interest
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    # 1️⃣ Create two coaches with proper UUIDs
    coach1 = Coach(
        full_name="Coach A",
        phone="+254725715778",
        whatsapp_number="+254725715778",
        user_id=uuid.uuid4()
    )
    coach2 = Coach(
        full_name="Coach B",
        phone="+254791320979",
        whatsapp_number="+254791320979",
        user_id=uuid.uuid4()
    )
    db.session.add_all([coach1, coach2])
    db.session.commit()

    # 2️⃣ Create a team for each coach
    team1 = Team(name="Eagles FC", coach_id=coach1.id)
    team2 = Team(name="Falcons FC", coach_id=coach2.id)
    db.session.add_all([team1, team2])
    db.session.commit()

    # 3️⃣ Create match interest and send WhatsApp
    interest_data = {
        "requesting_team_id": team1.id,
        "target_team_id": team2.id,
        "proposed_date": datetime.now() + timedelta(days=2),
        "proposed_venue": "Local Stadium",
        "message": "Friendly match request"
    }
    interest = create_match_interest(interest_data, coach1)
    print("Match interest created:", interest.id)
