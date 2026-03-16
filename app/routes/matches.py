from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import joinedload
from app.services.auth_service import get_current_coach, get_current_user
from app.services.match_service import schedule_match, start_match, finish_match, create_tournament_matches
from app.models.match import Match
from app.models.tournament import Tournament
from app.models.enums import MatchStatus
from app.models.admin import Admin
from app.extensions.db import db


bp = Blueprint("matches", __name__, url_prefix="/api/matches")
match_bp = Blueprint(
    "tournament_matches",
    __name__,
    url_prefix="/api/tournaments/<uuid:tournament_id>/matches"
)

@bp.put("/<uuid:match_id>", strict_slashes=False)
def update_match_details(match_id):
    try:
        # Allow both coaches and admins to update matches
        user = get_current_user()
        if isinstance(user, Admin):
            # Admin can update any match
            pass
        else:
            # Coach can only update matches they own
            match = Match.query.get_or_404(match_id)
            if str(match.home_team.coach_id) != str(user.id) and str(match.away_team.coach_id) != str(user.id):
                return jsonify({"error": "You don't have permission to update this match"}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 401

    match = Match.query.get_or_404(match_id)
    data = request.json

    # Update allowed fields
    if 'home_score' in data:
        match.home_score = data['home_score']
    if 'away_score' in data:
        match.away_score = data['away_score']
    if 'status' in data:
        match.status = MatchStatus(data['status'])
    if 'venue' in data:
        match.venue = data['venue']

    db.session.commit()
    return jsonify(match.to_dict()), 200


@bp.delete("/<uuid:match_id>", strict_slashes=False)
def delete_match(match_id):
    try:
        # Allow both coaches and admins to delete matches
        user = get_current_user()
        if isinstance(user, Admin):
            # Admin can delete any match
            pass
        else:
            # Coach can only delete matches they own
            match = Match.query.get_or_404(match_id)
            if str(match.home_team.coach_id) != str(user.id) and str(match.away_team.coach_id) != str(user.id):
                return jsonify({"error": "You don't have permission to delete this match"}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 401

    match = Match.query.get_or_404(match_id)
    
    # Delete associated events first
    from app.models.match_event import MatchEvent
    MatchEvent.query.filter_by(match_id=match_id).delete()
    
    db.session.delete(match)
    db.session.commit()
    return jsonify({"message": "Match deleted successfully"}), 200


@bp.patch("/<uuid:match_id>/start", strict_slashes=False)
def start(match_id):
    try:
        get_current_coach()
    except Exception as e:
        return jsonify({"error": str(e)}), 401
    match = Match.query.get_or_404(match_id)
    return jsonify(start_match(match).to_dict())


@bp.patch("/<uuid:match_id>/pause", strict_slashes=False)
def pause(match_id):
    try:
        get_current_coach()
    except Exception as e:
        return jsonify({"error": str(e)}), 401
    match = Match.query.get_or_404(match_id)
    if match.status != MatchStatus.live:
        return jsonify({"error": "Match is not live"}), 400
    match.status = MatchStatus.paused
    # Optionally, record the paused time, but for now, just change status
    db.session.commit()
    return jsonify(match.to_dict())


@bp.patch("/<uuid:match_id>/resume", strict_slashes=False)
def resume(match_id):
    try:
        get_current_coach()
    except Exception as e:
        return jsonify({"error": str(e)}), 401
    match = Match.query.get_or_404(match_id)
    if match.status != MatchStatus.paused:
        return jsonify({"error": "Match is not paused"}), 400
    match.status = MatchStatus.live
    db.session.commit()
    return jsonify(match.to_dict())


@bp.patch("/<uuid:match_id>/finish", strict_slashes=False)
def finish(match_id):
    print(f"Finish match route called for match_id: {match_id}")
    try:
        get_current_coach()
    except Exception as e:
        return jsonify({"error": str(e)}), 401
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


@bp.get("/h2h/<uuid:team1_id>/<uuid:team2_id>")
def get_head_to_head(team1_id, team2_id):
    # Public endpoint
    from sqlalchemy import and_, or_
    matches = Match.query.options(
        joinedload(Match.home_team),
        joinedload(Match.away_team)
    ).filter(
        and_(
            or_(
                and_(Match.home_team_id == team1_id, Match.away_team_id == team2_id),
                and_(Match.home_team_id == team2_id, Match.away_team_id == team1_id)
            ),
            Match.status == MatchStatus.finished
        )
    ).all()

    team1_wins = 0
    team2_wins = 0
    draws = 0

    for match in matches:
        if match.home_team_id == team1_id:
            if match.home_score > match.away_score:
                team1_wins += 1
            elif match.home_score < match.away_score:
                team2_wins += 1
            else:
                draws += 1
        else:
            if match.away_score > match.home_score:
                team1_wins += 1
            elif match.away_score < match.home_score:
                team2_wins += 1
            else:
                draws += 1

    return jsonify({
        'team1_id': str(team1_id),
        'team2_id': str(team2_id),
        'team1_wins': team1_wins,
        'team2_wins': team2_wins,
        'draws': draws,
        'total_matches': len(matches),
        'matches': [m.to_dict() for m in matches]
    })


@bp.get("/<uuid:match_id>")
def get_match(match_id):
    # Public endpoint: allow viewing match details without authentication
    match = Match.query.options(
        joinedload(Match.events),
        joinedload(Match.home_team),
        joinedload(Match.away_team)
    ).get_or_404(match_id)
    return jsonify(match.to_dict())


@bp.get("/my-matches")
def my_matches():
    """Get matches where the coach's teams are participating"""
    try:
        coach = get_current_coach()
    except Exception as e:
        return jsonify({"error": str(e)}), 401

    status_filter = request.args.get('status')
    from app.models.enums import MatchStatus
    from sqlalchemy.orm import joinedload

    query = Match.query.options(
        joinedload(Match.events),
        joinedload(Match.home_team),
        joinedload(Match.away_team)
    )

    # Filter by coach's teams
    team_ids = [str(team.id) for team in coach.teams]
    query = query.filter(
        Match.home_team_id.in_(team_ids) | Match.away_team_id.in_(team_ids)
    )

    if status_filter:
        if status_filter == 'live':
            query = query.filter(Match.status == MatchStatus.live)
        elif status_filter == 'scheduled':
            query = query.filter(Match.status == MatchStatus.scheduled)
        elif status_filter == 'finished':
            query = query.filter(Match.status == MatchStatus.finished)
        elif status_filter == 'paused':
            query = query.filter(Match.status == MatchStatus.paused)

    matches = query.order_by(Match.match_date.desc()).limit(50).all()
    return jsonify([m.to_dict() for m in matches])


@match_bp.post("")
def create_matches(tournament_id):
    coach = get_current_coach()
    data = request.json
    matches = create_tournament_matches(tournament_id, data["matches"])
    return jsonify(matches), 201


@match_bp.get("")
def list_tournament_matches(tournament_id):
    # Public listing of matches for a tournament with optional status filter
    status = request.args.get('status')
    from app.models.enums import MatchStatus

    qry = Match.query.options(
        joinedload(Match.home_team),
        joinedload(Match.away_team)
    ).filter(Match.competition_id == tournament_id)

    if status:
        if status == 'upcoming':
            qry = qry.filter(Match.status == MatchStatus.scheduled)
        elif status == 'live':
            qry = qry.filter(Match.status == MatchStatus.live)
        elif status == 'finished':
            qry = qry.filter(Match.status == MatchStatus.finished)

    matches = qry.order_by(Match.match_date.asc()).all()
    return jsonify([m.to_dict() for m in matches])