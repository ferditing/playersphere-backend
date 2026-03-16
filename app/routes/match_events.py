from flask import Blueprint, request, jsonify
from app.extensions.db import db
from app.services.auth_service import get_current_coach, get_current_user
from app.models.match_event import MatchEvent
from app.models.match import Match
from app.models.enums import MatchStatus
from app.models.player_stats import PlayerStats
from app.models.admin import Admin

bp = Blueprint("match_events", __name__, url_prefix="/api/match-events")

# Also register routes under /api/matches/{match_id}/events for convenience
matches_bp = Blueprint("match_events_matches", __name__, url_prefix="/api/matches/<uuid:match_id>/events")

@bp.get("/<uuid:match_id>")
def get_match_events(match_id):
    # Public endpoint: allow unauthenticated users to view match info.
    # Only return detailed events if the match has started or finished.
    from sqlalchemy.orm import joinedload
    match = Match.query.options(
        joinedload(Match.home_team),
        joinedload(Match.away_team)
    ).get_or_404(match_id)
    events = []
    if match.status == MatchStatus.live or match.status == MatchStatus.finished:
        events = MatchEvent.query.filter_by(match_id=match_id).order_by(MatchEvent.minute).all()

    return jsonify({
        'match': match.to_dict(),
        'events': [event.to_dict() for event in events]
    })

@bp.post("/")
def create_match_event():
    # Allow both coaches and admins to create events
    user = get_current_user()
    data = request.json

    # Validate required fields
    required_fields = ["match_id", "team_id", "event_type", "minute"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"Missing or empty required field: {field}"}), 400

    # Validate minute is an integer
    try:
        minute = int(data["minute"])
        if minute < 1 or minute > 120:
            return jsonify({"error": "Minute must be between 1 and 120"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Minute must be a valid integer"}), 400

    # Verify the match exists
    match = Match.query.get_or_404(data["match_id"])

    # For coaches, verify they own one of the teams
    if not isinstance(user, Admin):
        if str(match.home_team.coach_id) != str(user.id) and str(match.away_team.coach_id) != str(user.id):
            return jsonify({"error": "You don't have permission to add events to this match"}), 403

    if match.status.value != 'live' and match.status.value != 'finished':
        return jsonify({"error": "Match is not active"}), 400

    event = MatchEvent(
        match_id=data["match_id"],
        team_id=data["team_id"],
        player_id=data.get("player_id"),
        event_type=data["event_type"],
        minute=minute,  # Use the validated integer
        additional_info=data.get("additional_info", {})
    )

    # Update match score based on event type
    if data["event_type"] == "goal":
        if str(data["team_id"]) == str(match.home_team_id):
            match.home_score += 1
        elif str(data["team_id"]) == str(match.away_team_id):
            match.away_score += 1
        db.session.add(match)
    elif data["event_type"] == "penalty_goal":
        if str(data["team_id"]) == str(match.home_team_id):
            match.home_score += 1
        elif str(data["team_id"]) == str(match.away_team_id):
            match.away_score += 1
        db.session.add(match)
    elif data["event_type"] == "own_goal":
        # Own goal means the opposing team gets the point
        if str(data["team_id"]) == str(match.home_team_id):
            match.away_score += 1
        elif str(data["team_id"]) == str(match.away_team_id):
            match.home_score += 1
        db.session.add(match)

    # Update match current_minute if this event is at a later minute
    if minute > match.current_minute:
        match.current_minute = minute
        db.session.add(match)

    db.session.add(event)

    # Update PlayerStats immediately for this event (so public stats reflect changes)
    if data.get("player_id"):
        try:
            pid = data.get("player_id")
            ps = PlayerStats.query.filter_by(player_id=pid).first()
            if not ps:
                ps = PlayerStats(player_id=pid)
                db.session.add(ps)

            et = data.get("event_type")
            if et in ("goal", "penalty_goal"):
                ps.goals = (ps.goals or 0) + 1
            elif et == "yellow_card":
                ps.yellow_cards = (ps.yellow_cards or 0) + 1
            elif et == "red_card":
                ps.red_cards = (ps.red_cards or 0) + 1
        except Exception as _:
            # don't block event creation on stats update
            pass

    db.session.commit()

    return jsonify(event.to_dict()), 201

@matches_bp.post("/")
@matches_bp.post("")
def create_match_event_for_match(match_id):
    # Allow both coaches and admins to create events
    user = get_current_user()
    data = request.json

    # Validate required fields
    required_fields = ["team_id", "event_type", "minute"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"Missing or empty required field: {field}"}), 400

    # Validate minute is an integer
    try:
        minute = int(data["minute"])
        if minute < 1 or minute > 120:
            return jsonify({"error": "Minute must be between 1 and 120"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Minute must be a valid integer"}), 400

    # Set the match_id from the URL
    data["match_id"] = str(match_id)

    # Verify the match exists
    match = Match.query.get_or_404(data["match_id"])

    # For coaches, verify they own one of the teams
    if not isinstance(user, Admin):
        if str(match.home_team.coach_id) != str(user.id) and str(match.away_team.coach_id) != str(user.id):
            return jsonify({"error": "You don't have permission to add events to this match"}), 403

    if match.status.value != 'live' and match.status.value != 'finished':
        return jsonify({"error": "Match is not active"}), 400

    event = MatchEvent(
        match_id=data["match_id"],
        team_id=data["team_id"],
        player_id=data.get("player_id"),
        event_type=data["event_type"],
        minute=minute,  # Use the validated integer
        additional_info=data.get("additional_info", {})
    )
    db.session.add(event)

    # Update match scores for goals
    if data["event_type"] == "goal":
        if str(data["team_id"]) == str(match.home_team_id):
            match.home_score += 1
        elif str(data["team_id"]) == str(match.away_team_id):
            match.away_score += 1
        db.session.add(match)
    elif data["event_type"] == "penalty_goal":
        if str(data["team_id"]) == str(match.home_team_id):
            match.home_score += 1
        elif str(data["team_id"]) == str(match.away_team_id):
            match.away_score += 1
        db.session.add(match)
    elif data["event_type"] == "own_goal":
        # Own goal means the opposing team gets the point
        if str(data["team_id"]) == str(match.home_team_id):
            match.away_score += 1
        elif str(data["team_id"]) == str(match.away_team_id):
            match.home_score += 1
        db.session.add(match)

    # Update match current_minute if this event is at a later minute
    if minute > match.current_minute:
        match.current_minute = minute
        db.session.add(match)

    # Update PlayerStats immediately for this event (so public stats reflect changes)
    if data.get("player_id"):
        try:
            pid = data.get("player_id")
            ps = PlayerStats.query.filter_by(player_id=pid).first()
            if not ps:
                ps = PlayerStats(player_id=pid)
                db.session.add(ps)

            et = data.get("event_type")
            if et in ("goal", "penalty_goal"):
                ps.goals = (ps.goals or 0) + 1
            elif et == "yellow_card":
                ps.yellow_cards = (ps.yellow_cards or 0) + 1
            elif et == "red_card":
                ps.red_cards = (ps.red_cards or 0) + 1
        except Exception as _:
            # don't block event creation on stats update
            pass

    db.session.commit()

    return jsonify(event.to_dict()), 201

@bp.delete("/<uuid:event_id>")
def delete_match_event(event_id):
    coach = get_current_coach()
    event = MatchEvent.query.get_or_404(event_id)

    # Verify the match exists and coach owns one of the teams
    match = event.match
    if str(match.home_team.coach_id) != str(coach.id) and str(match.away_team.coach_id) != str(coach.id):
        return jsonify({"error": "You don't have permission to delete events from this match"}), 403

    if match.status.value != 'live':
        return jsonify({"error": "Match is not active"}), 400

    # Adjust match score based on event type
    if event.event_type.value in ("goal", "penalty_goal"):
        if str(event.team_id) == str(match.home_team_id):
            match.home_score = max(0, match.home_score - 1)
        elif str(event.team_id) == str(match.away_team_id):
            match.away_score = max(0, match.away_score - 1)
        db.session.add(match)
    elif event.event_type.value == "own_goal":
        # Own goal: when deleting, reverse the effect
        if str(event.team_id) == str(match.home_team_id):
            match.away_score = max(0, match.away_score - 1)
        elif str(event.team_id) == str(match.away_team_id):
            match.home_score = max(0, match.home_score - 1)
        db.session.add(match)

    # Adjust PlayerStats to remove the effect of this event if applicable
    if event.player_id:
        try:
            ps = PlayerStats.query.filter_by(player_id=event.player_id).first()
            if ps:
                ev = event.event_type.value if hasattr(event.event_type, 'value') else str(event.event_type)
                if ev in ("goal", "penalty_goal") and ps.goals:
                    ps.goals = max(0, ps.goals - 1)
                elif ev == "yellow_card" and ps.yellow_cards:
                    ps.yellow_cards = max(0, ps.yellow_cards - 1)
                elif ev == "red_card" and ps.red_cards:
                    ps.red_cards = max(0, ps.red_cards - 1)
        except Exception:
            pass

    db.session.delete(event)
    db.session.commit()

    return jsonify({"message": "Event deleted successfully"})