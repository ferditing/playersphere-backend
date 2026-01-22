from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import joinedload
from app.services.auth_service import get_current_coach
from app.services.match_service import schedule_match, start_match, finish_match
from app.models.match import Match
from app.extensions.db import db

bp = Blueprint("matches", __name__, url_prefix="/matches")

@bp.post("/")
def create_match():
    coach = get_current_coach()
    match = schedule_match(request.json, coach.id)
    return jsonify(match.to_dict()), 201


@bp.patch("/<uuid:match_id>/start")
def start(match_id):
    get_current_coach()
    match = Match.query.get_or_404(match_id)
    return jsonify(start_match(match).to_dict())


@bp.patch("/<uuid:match_id>/finish")
def finish(match_id):
    print(f"Finish match route called for match_id: {match_id}")
    get_current_coach()
    match = Match.query.get_or_404(match_id)
    print(f"Found match {match_id} with status: {match.status}")
    try:
        result = finish_match(match)
        print(f"Finish match completed for {match_id}, returning status: {result.status}")
        print(f"Match {match_id} final status value: {result.status.value if result.status else None}")
        # Debug: log started_at to ensure backend cleared it
        try:
            print(f"Match {match_id} started_at after finish: {result.started_at}")
        except Exception as _:
            print(f"Match {match_id} started_at not available in result object")
        return jsonify(result.to_dict())
    except Exception as e:
        print(f"Error in finish route for match {match_id}: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.get("/<uuid:match_id>")
def get_match(match_id):
    # Public endpoint: allow viewing match details without authentication
    match = Match.query.options(
        joinedload(Match.events),
        joinedload(Match.home_team),
        joinedload(Match.away_team)
    ).get_or_404(match_id)
    return jsonify(match.to_dict())


@bp.put("/<uuid:match_id>")
def update_match(match_id):
    coach = get_current_coach()
    match = Match.query.get_or_404(match_id)

    # Check if coach owns one of the teams
    if str(match.home_team.coach_id) != str(coach.id) and str(match.away_team.coach_id) != str(coach.id):
        abort(403, "You don't have permission to update this match")

    data = request.json
    # Update allowed fields
    if "venue" in data:
        match.venue = data["venue"]
    if "match_date" in data:
        match.match_date = data["match_date"]

    from app.extensions.db import db
    db.session.commit()
    return jsonify(match.to_dict())
