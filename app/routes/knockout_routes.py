from flask import Blueprint, request, jsonify
from app.services.knockout_service import KnockoutService
from app.services.match_service import generate_round_robin
from app.models.tournament_team import TournamentTeam
from app.models.tournament import Tournament

knockout_bp = Blueprint("knockout", __name__, url_prefix="/tournaments")


@knockout_bp.post("/<uuid:tournament_id>/qualify")
def qualify_teams(tournament_id):
    data = request.json
    qualified = KnockoutService.qualify_teams(
        tournament_id,
        slots=data["slots"]
    )
    return jsonify(qualified), 200


@knockout_bp.post("/<uuid:tournament_id>/bracket")
def generate_bracket(tournament_id):
    data = request.json
    matches = KnockoutService.generate_bracket(
        tournament_id,
        qualified_teams=data["teams"],
        match_date=data["match_date"]
    )
    return jsonify(matches), 201


@knockout_bp.post("/<uuid:tournament_id>/generate-roundrobin")
def generate_roundrobin(tournament_id):
    data = request.json
    teams = data.get("teams", [])
    start_date = data.get("start_date")
    interval = data.get("interval_days", 7)
    venue = data.get("venue")

    if not start_date or not teams:
        return jsonify({"error": "start_date and teams are required"}), 400

    # Validate tournament exists and type is appropriate
    tournament = Tournament.query.get(tournament_id)
    if not tournament:
        return jsonify({"error": "Tournament not found"}), 404
    if tournament.tournament_type == 'knockout':
        return jsonify({"error": "Round-robin generation not allowed for knockout tournaments"}), 400

    # Validate provided team IDs belong to this tournament (have been accepted/registered)
    provided = set(teams)
    found = TournamentTeam.query.filter(TournamentTeam.tournament_id == tournament_id).filter(TournamentTeam.team_id.in_(list(provided))).all()
    found_ids = set([str(f.team_id) for f in found])
    missing = list(provided - found_ids)
    if missing:
        return jsonify({"error": "Some teams are not part of this tournament", "missing": missing}), 400

    matches = generate_round_robin(
        tournament_id,
        teams,
        start_date,
        interval_days=interval,
        venue=venue,
    )

    return jsonify(matches), 201
