from flask import Blueprint, request, jsonify
from app.extensions.db import db
from app.services.auth_service import get_current_coach
from app.models.message import Message

bp = Blueprint("messages", __name__, url_prefix="/messages")

@bp.get("/")
def get_messages():
    coach = get_current_coach()
    messages = Message.query.filter(
        (Message.sender_id == coach.id) | (Message.recipient_id == coach.id)
    ).order_by(Message.created_at.desc()).all()

    return jsonify([msg.to_dict() for msg in messages])

@bp.post("/")
def create_message():
    coach = get_current_coach()
    data = request.json

    message = Message(
        sender_id=coach.id,
        recipient_id=data["recipient_id"],
        content=data["content"]
    )

    db.session.add(message)
    db.session.commit()

    return jsonify(message.to_dict()), 201