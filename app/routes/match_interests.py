from flask import Blueprint, request, jsonify
from app.extensions.db import db
from app.services.auth_service import get_current_coach
from app.services.whatsapp_service import send_whatsapp_message, send_whatsapp_template_message, _get_config
import logging
import os
from urllib.parse import quote_plus
from app.models.match_interest import MatchInterest
from app.models.match import Match
from app.models.enums import MatchInterestStatus

bp = Blueprint("match_interests", __name__, url_prefix="/match-interests")

@bp.get("")
def get_match_interests():
    coach = get_current_coach()
    status = request.args.get('status')
    
    query = MatchInterest.query.join(
        MatchInterest.target_team
    ).filter(
        (MatchInterest.requesting_coach_id == coach.id) |
        (MatchInterest.target_team.has(coach_id=coach.id))
    )
    
    if status:
        query = query.filter(MatchInterest.status == status)
    
    interests = query.order_by(MatchInterest.created_at.desc()).all()

    return jsonify([interest.to_dict() for interest in interests])

@bp.post("")
def create_match_interest():
    coach = get_current_coach()
    data = request.json

    interest = MatchInterest(
        requesting_coach_id=coach.id,
        requesting_team_id=data["requesting_team_id"],
        target_team_id=data["target_team_id"],
        proposed_date=data["proposed_date"],
        proposed_venue=data.get("proposed_venue"),
        message=data.get("message")
    )

    db.session.add(interest)
    db.session.commit()

    # Try to send a WhatsApp notification to the target coach if they have a number
    try:
        # Debug: log whether WhatsApp credentials are visible to this process
        app_logger = logging.getLogger('playersphere')
        token, phone_id, base_url = _get_config()
        app_logger.debug('WhatsApp env presence before send: token=%s, phone_id=%s, base_url=%s', bool(token), bool(phone_id), bool(base_url))
        target_coach = None
        if interest.target_team and getattr(interest.target_team, 'coach', None):
            target_coach = interest.target_team.coach

        if target_coach:
            to_number = (target_coach.whatsapp_number or target_coach.phone or '').strip()
            if to_number:
                # Build frontend links for accept/decline/edit
                frontend = os.getenv('FRONTEND_URL', 'http://localhost:3000').rstrip('/')
                accept_link = f"{frontend}/match-requests/{interest.id}/respond?status=accepted"
                decline_link = f"{frontend}/match-requests/{interest.id}/respond?status=declined"
                edit_link = f"{frontend}/match-requests/{interest.id}/edit"

                # Use template if available; fallback to plain text
                template_name = 'match_request_notification'
                # Parameters: coach name, requesting team, requesting coach, date, venue, accept link, edit link
                coach_name = target_coach.full_name if getattr(target_coach, 'full_name', None) else 'Coach'
                req_team = interest.requesting_team.name if interest.requesting_team else 'a team'
                req_coach = interest.requesting_coach.full_name if interest.requesting_coach else 'Coach'
                proposed_date = interest.proposed_date.isoformat() if interest.proposed_date else ''
                venue = interest.proposed_venue or 'TBD'

                try:
                    # Try template send first
                    send_whatsapp_template_message(
                        to_number,
                        template_name,
                        [coach_name, req_team, req_coach, proposed_date, venue, accept_link, edit_link]
                    )
                except Exception as wa_err:
                    # Fallback to plain text message if template send fails
                    app_logger = __import__('logging').getLogger('playersphere')
                    app_logger.exception('Template send failed, falling back to text: %s', wa_err)
                    try:
                        text_msg = (
                            f"Hello {coach_name},\n"
                            f"Match request from {req_team} (sent by {req_coach})\n"
                            f"Date: {proposed_date}\nVenue: {venue}\n"
                            f"Accept: {accept_link}\nEdit: {edit_link}"
                        )
                        send_whatsapp_message(to_number, text_msg)
                    except Exception as wa_err2:
                        app_logger.exception('Failed to send WhatsApp notification: %s', wa_err2)
    except Exception:
        # Protect the create endpoint from any unexpected errors while trying to notify
        pass

    return jsonify(interest.to_dict()), 201

@bp.put("/<uuid:interest_id>/respond")
def respond_to_interest(interest_id):
    coach = get_current_coach()
    data = request.json

    interest = MatchInterest.query.get_or_404(interest_id)

    # Check if coach owns the target team
    # Add debug logging to help diagnose 403 responses
    app_logger = logging.getLogger('playersphere')
    target_coach_id = None
    try:
        if interest.target_team:
            target_coach_id = str(interest.target_team.coach_id)
    except Exception:
        target_coach_id = None

    app_logger.debug('respond_to_interest: auth_coach_id=%s, target_coach_id=%s, requesting_coach_id=%s, interest_id=%s',
                     str(getattr(coach, 'id', None)), target_coach_id, str(interest.requesting_coach_id), str(interest.id))

    if not target_coach_id or target_coach_id != str(coach.id):
        app_logger.warning('Unauthorized respond attempt: coach=%s interest=%s target_coach=%s', coach.id, interest.id, target_coach_id)
        return jsonify({"error": "You don't have permission to respond to this interest"}), 403

    interest.status = data["status"]
    interest.responded_at = db.func.now()

    # If accepted, create the match
    if data["status"] == "accepted":
        match = Match(
            home_team_id=interest.requesting_team_id,
            away_team_id=interest.target_team_id,
            match_date=interest.proposed_date,
            venue=interest.proposed_venue,
            status="scheduled",
            country="Kenya"
        )
        db.session.add(match)

    db.session.commit()
    return jsonify(interest.to_dict())


@bp.put("/<uuid:interest_id>")
def update_match_interest(interest_id):
    """Allow the requesting coach or the target coach to edit the proposed date/venue/message."""
    coach = get_current_coach()
    data = request.json

    interest = MatchInterest.query.get_or_404(interest_id)

    # Allow either the requesting coach or the target team's coach to edit
    target_coach_id = None
    if interest.target_team and getattr(interest.target_team, 'coach_id', None):
        target_coach_id = str(interest.target_team.coach_id)

    if not (str(interest.requesting_coach_id) == str(coach.id) or (target_coach_id and target_coach_id == str(coach.id))):
        return jsonify({"error": "You don't have permission to edit this interest"}), 403

    # Update allowable fields
    if 'proposed_date' in data:
        interest.proposed_date = data['proposed_date']
    if 'proposed_venue' in data:
        interest.proposed_venue = data.get('proposed_venue')
    if 'message' in data:
        interest.message = data.get('message')

    db.session.commit()
    return jsonify(interest.to_dict())