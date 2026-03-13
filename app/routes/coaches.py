from flask import Blueprint, request, jsonify
from app.extensions.db import db
from app.services.auth_service import get_current_coach, get_current_user
from app.models.coach import Coach
from app.models.admin import Admin
from app.models.match_interest import MatchInterest
from app.models.message import Message
from app.models.tournament import Tournament

bp = Blueprint("coaches", __name__, url_prefix="/api/coaches")

@bp.post("/", strict_slashes=False)
def create_coach():
    """Admin endpoint to create a new coach"""
    try:
        user = get_current_user()
        
        # Verify admin access
        if not isinstance(user, Admin):
            return jsonify({"error": "Only admins can create coaches"}), 403
        
        data = request.get_json() or {}
        
        # Validate required fields
        if not data.get("full_name"):
            return jsonify({"error": "Full name is required"}), 400
        if not data.get("email"):
            return jsonify({"error": "Email is required"}), 400
        if not data.get("phone"):
            return jsonify({"error": "Phone number is required"}), 400
        if not data.get("password"):
            return jsonify({"error": "Password is required"}), 400
        
        # Check if email already exists
        if Coach.query.filter_by(email=data.get("email")).first():
            return jsonify({"error": "Email already exists"}), 400
        
        # Check if phone already exists
        if Coach.query.filter_by(phone=data.get("phone")).first():
            return jsonify({"error": "Phone number already exists"}), 400
        
        # Create new coach
        coach = Coach(
            full_name=data.get("full_name"),
            email=data.get("email"),
            phone=data.get("phone"),
            whatsapp_number=data.get("whatsapp_number"),
            country=data.get("country", "Kenya"),
            region=data.get("region"),
            city=data.get("city"),
            county_id=data.get("county_id"),
            created_by_admin_id=user.id
        )
        
        coach.set_password(data.get("password"))
        
        db.session.add(coach)
        db.session.commit()
        
        return jsonify(coach.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@bp.get("/", strict_slashes=False)
def list_coaches():
    """List all coaches. Only admins can do this."""
    try:
        user = get_current_user()
        
        if not isinstance(user, Admin):
            return jsonify({"error": "Only admins can list coaches"}), 403
        
        coaches = Coach.query.all()
        return jsonify([c.to_dict() for c in coaches]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@bp.delete("/<uuid:coach_id>", strict_slashes=False)
def delete_coach(coach_id):
    """Delete a coach. Only admins can do this."""
    try:
        user = get_current_user()
        if not isinstance(user, Admin):
            return jsonify({"error": "Only admins can delete coaches"}), 403

        coach = Coach.query.get(coach_id)
        if not coach:
            return jsonify({"error": "Coach not found"}), 404

        # Prevent deleting coach who created tournaments (too important to lose)
        if Tournament.query.filter_by(created_by=coach_id).first():
            return jsonify({"error": "Cannot delete coach who created tournaments"}), 400

        # Delete all match interests sent by this coach
        MatchInterest.query.filter_by(requesting_coach_id=coach_id).delete()

        # Delete all messages sent or received by this coach
        Message.query.filter((Message.sender_id == coach_id) | (Message.recipient_id == coach_id)).delete()

        db.session.delete(coach)
        db.session.commit()
        return jsonify({"message": "Coach deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401

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