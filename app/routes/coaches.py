from flask import Blueprint, request, jsonify
from app.extensions.db import db
from app.services.auth_service import get_current_coach

bp = Blueprint("coaches", __name__, url_prefix="/coaches")

@bp.put("/profile")
def update_profile():
    coach = get_current_coach()
    data = request.json

    # Update coach fields
    coach.full_name = data.get("full_name", coach.full_name)
    coach.phone = data.get("phone", coach.phone)
    coach.whatsapp_number = data.get("whatsapp_number", coach.whatsapp_number)
    coach.country = data.get("country", coach.country)
    coach.region = data.get("region", coach.region)
    coach.city = data.get("city", coach.city)

    db.session.commit()
    return jsonify(coach.to_dict())