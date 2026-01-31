from flask import Blueprint, request, jsonify
from app.extensions.db import db
from app.services.auth_service import get_current_coach
from app.models.match_event import MatchEvent
from app.models.match import Match
from app.models.enums import MatchStatus
from app.models.player_stats import PlayerStats

bp = Blueprint("match_events", __name__, url_prefix="/match-events")

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
    coach = get_current_coach()
    data = request.json

    # Verify the match exists and coach owns one of the teams
    match = Match.query.get_or_404(data["match_id"])
    if str(match.home_team.coach_id) != str(coach.id) and str(match.away_team.coach_id) != str(coach.id):
        return jsonify({"error": "You don't have permission to add events to this match"}), 403

    event = MatchEvent(
        match_id=data["match_id"],
        team_id=data["team_id"],
        player_id=data.get("player_id"),
        event_type=data["event_type"],
        minute=data["minute"],
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
    if data["minute"] > match.current_minute:
        match.current_minute = data["minute"]
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

@bp.delete("/<uuid:event_id>")
def delete_match_event(event_id):
    coach = get_current_coach()
    event = MatchEvent.query.get_or_404(event_id)

    # Verify coach owns the team that created the event
    if str(event.team.coach_id) != str(coach.id):
        return jsonify({"error": "You don't have permission to delete this event"}), 403

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