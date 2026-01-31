from flask import Blueprint, jsonify
from app.services.player_stats_service import PlayerStatsService

stats_bp = Blueprint("stats", __name__, url_prefix="/tournaments")


@stats_bp.get("/<uuid:tournament_id>/stats/top-scorers")
def top_scorers(tournament_id):
    data = PlayerStatsService.top_scorers(tournament_id)
    return jsonify(data), 200


@stats_bp.get("/<uuid:tournament_id>/stats/discipline")
def discipline_table(tournament_id):
    data = PlayerStatsService.discipline_table(tournament_id)
    return jsonify(data), 200
