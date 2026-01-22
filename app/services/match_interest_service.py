from app.extensions.db import db
from app.models.match_interest import MatchInterest
from app.models.team import Team
from app.models.coach import Coach
from app.services.whatsapp_service import send_whatsapp_message

def create_match_interest(data, requesting_coach):
    """
    Create a match interest and send WhatsApp notification to target coach.
    """
    # 1️⃣ Create the MatchInterest
    interest = MatchInterest(
        requesting_coach_id=requesting_coach.id,
        requesting_team_id=data["requesting_team_id"],
        target_team_id=data["target_team_id"],
        proposed_date=data["proposed_date"],
        proposed_venue=data.get("proposed_venue"),
        message=data.get("message", ""),
        status="pending"
    )
    db.session.add(interest)
    db.session.commit()

    # 2️⃣ WhatsApp notification
    target_team = Team.query.get(data["target_team_id"])
    target_coach = Coach.query.get(target_team.coach_id)

    if target_coach and target_coach.whatsapp_number:
        requesting_team = Team.query.get(data["requesting_team_id"])
        text = (
            f"⚽ Match Request\n\n"
            f"From: {requesting_team.name}\n"
            f"Date: {data['proposed_date']}\n"
            f"Venue: {data.get('proposed_venue', 'TBD')}\n\n"
            f"Reply ACCEPT or DECLINE in the app."
        )
        send_whatsapp_message(target_coach.whatsapp_number, text)

    return interest
