from flask import Blueprint, request, jsonify
from app.extensions.db import db
from app.models.ticket import Ticket
from app.services.auth_service import get_current_admin, get_current_coach

bp = Blueprint("tickets", __name__, url_prefix="/api/tickets")

@bp.get("/")
def get_tickets():
    # Only admins can view tickets
    admin = get_current_admin()
    tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    return jsonify([ticket.to_dict() for ticket in tickets])

@bp.post("/")
def create_ticket():
    # Coaches can create tickets
    coach = get_current_coach()
    data = request.json

    ticket = Ticket(
        from_name=coach.full_name,
        team_name=data.get("team", ""),
        subject=data["subject"],
        message=data["message"],
        ticket_type=data["type"]
    )

    db.session.add(ticket)
    db.session.commit()

    return jsonify(ticket.to_dict()), 201

@bp.put("/<uuid:ticket_id>")
def update_ticket(ticket_id):
    # Only admins can update tickets
    admin = get_current_admin()
    ticket = Ticket.query.get_or_404(ticket_id)
    data = request.json

    if "status" in data:
        ticket.status = data["status"]

    db.session.commit()
    return jsonify(ticket.to_dict())

@bp.delete("/<uuid:ticket_id>")
def delete_ticket(ticket_id):
    # Only admins can delete tickets
    admin = get_current_admin()
    ticket = Ticket.query.get_or_404(ticket_id)

    db.session.delete(ticket)
    db.session.commit()

    return "", 204