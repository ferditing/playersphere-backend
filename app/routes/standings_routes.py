from flask import Blueprint, jsonify
from app.services.standings_service import StandingsService
from app.services.live_updates_service import LiveUpdatesService

standings_bp = Blueprint("standings", __name__, url_prefix="/tournaments")


@standings_bp.get("/<uuid:tournament_id>/standings")
def get_standings(tournament_id):
    table = StandingsService.get_standings(tournament_id)
    return jsonify(table), 200


@standings_bp.get("/<uuid:tournament_id>/standings/live")
def live_standings(tournament_id):
    table = LiveUpdatesService.live_table(tournament_id)
    return jsonify(table), 200
