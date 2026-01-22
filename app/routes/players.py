from flask import Blueprint, request, jsonify, abort
from app.extensions.db import db
from app.services.auth_service import get_current_coach
from app.models.player import Player
from app.models.team import Team

bp = Blueprint("players", __name__, url_prefix="/players")

@bp.post("/")
def create_player():
    coach = get_current_coach()
    data = request.json

    team = Team.query.get_or_404(data["team_id"])
    if team.coach_id != coach.id:
        abort(403)

    player = Player(
        team_id=team.id,
        full_name=data["full_name"],
        date_of_birth=data["date_of_birth"],
        position=data["position"],
        jersey_number=data.get("jersey_number")
    )
    db.session.add(player)
    db.session.commit()
    return jsonify(player.to_dict()), 201


@bp.get("/<uuid:player_id>")
def get_player(player_id):
    coach = get_current_coach()
    player = Player.query.get_or_404(player_id)

    # Check if coach owns the player's team
    if player.team.coach_id != coach.id:
        abort(403)

    return jsonify(player.to_dict())


@bp.put("/<uuid:player_id>")
def update_player(player_id):
    coach = get_current_coach()
    player = Player.query.get_or_404(player_id)

    # Check if coach owns the player's team
    if player.team.coach_id != coach.id:
        abort(403)

    data = request.json
    # Update allowed fields
    if "full_name" in data:
        player.full_name = data["full_name"]
    if "date_of_birth" in data:
        player.date_of_birth = data["date_of_birth"]
    if "position" in data:
        player.position = data["position"]
    if "jersey_number" in data:
        player.jersey_number = data["jersey_number"]

    db.session.commit()
    return jsonify(player.to_dict())


@bp.delete("/<uuid:player_id>")
def delete_player(player_id):
    coach = get_current_coach()
    player = Player.query.get_or_404(player_id)

    # Check if coach owns the player's team
    if player.team.coach_id != coach.id:
        abort(403)

    db.session.delete(player)
    db.session.commit()
    return jsonify({"message": "Player deleted successfully"})
