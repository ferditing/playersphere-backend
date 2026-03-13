from flask import Blueprint, request, jsonify
from app.extensions.db import db
from app.services.auth_service import get_current_coach, get_current_coach_or_none, get_current_user
from app.models.team import Team
from app.models.admin import Admin
from app.models.coach import Coach

bp = Blueprint("teams", __name__, url_prefix="/api/teams")


@bp.post("/", strict_slashes=False)
def create_team():
    """Create a team. Coaches create their own, admins can assign to any coach."""
    try:
        user = get_current_user()
        data = request.get_json() or {}

        if "name" not in data:
            return jsonify({"error": "Team name is required"}), 400

        # Determine which coach owns this team
        if isinstance(user, Admin):
            # Admin creating team: must specify coach_id
            coach_id = data.get("coach_id")
            if not coach_id:
                return jsonify({"error": "coach_id is required for admins"}), 400
            
            # Verify coach exists
            coach = Coach.query.get(coach_id)
            if not coach:
                return jsonify({"error": "Coach not found"}), 404
        else:
            # Coach creating their own team
            coach = get_current_coach()
            if not coach:
                return jsonify({"error": "Unauthorized"}), 401
            coach_id = coach.id

        team = Team(
            coach_id=coach_id,
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
    except Exception as e:
        return jsonify({"error": str(e)}), 401


@bp.get("/", strict_slashes=False)
def my_teams():
    try:
        # Check if it's an admin token
        user = get_current_user()
        if isinstance(user, Admin):
            # Admins can see all teams (or filter by county if county_admin)
            if user.role == 'county_admin' and user.county_id:
                teams = Team.query.filter_by(county_id=user.county_id).all()
            else:
                # Super admin sees all teams
                teams = Team.query.all()
        else:
            # Coaches only see their own teams
            coach = get_current_coach()
            teams = Team.query.filter_by(coach_id=coach.id).all()
        
        return jsonify([t.to_dict() for t in teams]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401


@bp.put("/<uuid:team_id>/backup-emails", strict_slashes=False)
def update_backup_emails(team_id):
    try:
        coach = get_current_coach()
    except Exception as e:
        return jsonify({"error": str(e)}), 401
    team = Team.query.filter_by(id=team_id, coach_id=coach.id).first()

    if not team:
        return jsonify({"error": "Team not found"}), 404

    data = request.json
    team.backup_email_1 = data.get("backup_email_1")
    team.backup_email_2 = data.get("backup_email_2")
    team.backup_email_3 = data.get("backup_email_3")

    db.session.commit()
    return jsonify(team.to_dict())


@bp.get("/<uuid:team_id>/backup-email-verifications", strict_slashes=False)
def get_backup_email_verifications(team_id):
    try:
        coach = get_current_coach()
    except Exception as e:
        return jsonify({"error": str(e)}), 401
    team = Team.query.filter_by(id=team_id, coach_id=coach.id).first()

    if not team:
        return jsonify({"error": "Team not found"}), 404

    # For now, return empty list since we don't have verification model yet
    return jsonify([])


@bp.put("/<uuid:team_id>", strict_slashes=False)
def update_team(team_id):
    try:
        user = get_current_user()
    except Exception as e:
        return jsonify({"error": str(e)}), 401

    # Determine access: admins can update any team (and reassign coaches), coaches can only update their own teams
    team = None
    from app.models.admin import Admin

    if isinstance(user, Admin):
        team = Team.query.get(team_id)
    else:
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

    # Admins can reassign the team to a different coach (useful when deleting coaches)
    if isinstance(user, Admin) and "coach_id" in data:
        new_coach = Coach.query.get(data.get("coach_id"))
        if not new_coach:
            return jsonify({"error": "Coach not found"}), 404
        team.coach_id = new_coach.id

    db.session.commit()
    return jsonify(team.to_dict())


@bp.delete("/<uuid:team_id>", strict_slashes=False)
def delete_team(team_id):
    """Delete a team. Coaches can delete their own teams; admins can delete any."""
    try:
        user = get_current_user()
    except Exception as e:
        return jsonify({"error": str(e)}), 401

    # Determine if user is admin or coach
    team = None
    from app.models.admin import Admin

    if isinstance(user, Admin):
        # Admin can delete any team
        team = Team.query.get(team_id)
    else:
        # Coach can only delete their own team
        coach = get_current_coach()
        team = Team.query.filter_by(id=team_id, coach_id=coach.id).first()

    if not team:
        return jsonify({"error": "Team not found"}), 404

    # Prevent deleting teams that are referenced by existing matches.
    # Matches currently require non-null home_team_id and away_team_id.
    if getattr(team, 'home_matches', None) or getattr(team, 'away_matches', None):
        return jsonify({
            "error": "Cannot delete team while it has scheduled/recorded matches. Reassign or remove those matches first."
        }), 400

    db.session.delete(team)
    db.session.commit()
    return jsonify({"message": "Team deleted successfully"})


@bp.get("/<uuid:team_id>/players", strict_slashes=False)
def get_team_players(team_id):
    try:
        coach = get_current_coach()
    except Exception as e:
        return jsonify({"error": str(e)}), 401
    team = Team.query.filter_by(id=team_id, coach_id=coach.id).first()

    if not team:
        return jsonify({"error": "Team not found"}), 404

    players = team.players
    return jsonify([player.to_dict() for player in players])
