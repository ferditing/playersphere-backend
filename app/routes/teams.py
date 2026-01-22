from flask import Blueprint, request, jsonify
from app.extensions.db import db
from app.services.auth_service import get_current_coach
from app.models.team import Team

bp = Blueprint("teams", __name__, url_prefix="/teams")


@bp.post("/")
def create_team():
    coach = get_current_coach()
    if not coach:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}

    if "name" not in data:
        return jsonify({"error": "Team name is required"}), 400

    team = Team(
        coach_id=coach.id,
        name=data["name"],
        region=data.get("region"),
        city=data.get("city"),
        area=data.get("area"),
        team_type=data.get("team_type"),
        backup_email_1=data.get("backup_email_1"),
        backup_email_2=data.get("backup_email_2"),
    )

    db.session.add(team)
    db.session.commit()

    return jsonify(team.to_dict()), 201

    coach = get_current_coach()
    data = request.json

    team = Team(
        coach_id=coach.id,
        name=data["name"],
        region=data.get("region"),
        city=data.get("city"),
        area=data.get("area"),
        team_type=data.get("team_type"),
        backup_email_1=data.get("backup_email_1"),
        backup_email_2=data.get("backup_email_2")
    )
    db.session.add(team)
    db.session.commit()
    return jsonify(team.to_dict()), 201


@bp.get("/")
def my_teams():
    coach = get_current_coach()
    teams = Team.query.filter_by(coach_id=coach.id).all()
    return jsonify([t.to_dict() for t in teams])


@bp.put("/<uuid:team_id>/backup-emails")
def update_backup_emails(team_id):
    coach = get_current_coach()
    team = Team.query.filter_by(id=team_id, coach_id=coach.id).first()

    if not team:
        return jsonify({"error": "Team not found"}), 404

    data = request.json
    team.backup_email_1 = data.get("backup_email_1")
    team.backup_email_2 = data.get("backup_email_2")
    team.backup_email_3 = data.get("backup_email_3")

    db.session.commit()
    return jsonify(team.to_dict())


@bp.get("/<uuid:team_id>/backup-email-verifications")
def get_backup_email_verifications(team_id):
    coach = get_current_coach()
    team = Team.query.filter_by(id=team_id, coach_id=coach.id).first()

    if not team:
        return jsonify({"error": "Team not found"}), 404

    # For now, return empty list since we don't have verification model yet
    return jsonify([])


@bp.put("/<uuid:team_id>")
def update_team(team_id):
    coach = get_current_coach()
    team = Team.query.filter_by(id=team_id, coach_id=coach.id).first()

    if not team:
        return jsonify({"error": "Team not found"}), 404

    data = request.json
    # Update allowed fields
    if "name" in data:
        team.name = data["name"]
    if "region" in data:
        team.region = data["region"]
    if "city" in data:
        team.city = data["city"]
    if "area" in data:
        team.area = data["area"]
    if "team_type" in data:
        team.team_type = data["team_type"]

    db.session.commit()
    return jsonify(team.to_dict())


@bp.delete("/<uuid:team_id>")
def delete_team(team_id):
    coach = get_current_coach()
    team = Team.query.filter_by(id=team_id, coach_id=coach.id).first()

    if not team:
        return jsonify({"error": "Team not found"}), 404

    db.session.delete(team)
    db.session.commit()
    return jsonify({"message": "Team deleted successfully"})


@bp.get("/<uuid:team_id>/players")
def get_team_players(team_id):
    coach = get_current_coach()
    team = Team.query.filter_by(id=team_id, coach_id=coach.id).first()

    if not team:
        return jsonify({"error": "Team not found"}), 404

    players = team.players
    return jsonify([player.to_dict() for player in players])
