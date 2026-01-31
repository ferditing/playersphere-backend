from flask import Blueprint, request, jsonify
from app.services.tournament_service import TournamentService
from app.services.invite_service import InviteService
from app.services.auth_service import get_current_coach
from app.models.tournament import Tournament
from flask import current_app

tournament_bp = Blueprint("tournaments", __name__, url_prefix="/tournaments")


@tournament_bp.post("")
def create_tournament():
    data = request.json
    try:
        coach_id = get_current_coach().id
    except Exception as e:
        return jsonify({"error": str(e)}), 401

    tournament = TournamentService.create_tournament(data, coach_id=coach_id)
    return jsonify(tournament.to_dict()), 201



@tournament_bp.get('/my-tournaments')
def my_tournaments():
    try:
        coach = get_current_coach()
    except Exception as e:
        return jsonify({"error": str(e)}), 401

    tournaments = Tournament.query.filter_by(created_by=coach.id).all()
    return jsonify([t.to_dict() for t in tournaments])



@tournament_bp.get("")
def list_tournaments():
    # Public listing used by frontend public page. Support basic filters.
    args = request.args
    qry = Tournament.query
    ttype = args.get('type')
    status = args.get('status')
    if ttype:
        qry = qry.filter(Tournament.tournament_type == ttype)
    if status:
        qry = qry.filter(Tournament.status == status)

    tournaments = qry.order_by(Tournament.created_at.desc()).all()
    return jsonify([t.to_dict() for t in tournaments])


@tournament_bp.get("/<uuid:tournament_id>")
def get_tournament(tournament_id):
    t = Tournament.query.get_or_404(tournament_id)
    return jsonify(t.to_dict())


@tournament_bp.post("/<uuid:tournament_id>/invite")
def invite_team(tournament_id):
    data = request.json
    try:
        coach = get_current_coach()
    except Exception as e:
        return jsonify({"error": str(e)}), 401

    team_id = data.get('team_id')
    to_coach_id = None
    if team_id:
        from app.models.team import Team
        team = Team.query.get(team_id)
        if not team:
            return jsonify({"error": "Team not found"}), 404
        to_coach_id = team.coach_id

    invite = InviteService.send_invite(
        tournament_id=tournament_id,
        from_coach_id=coach.id,
        to_coach_id=to_coach_id,
        team_id=team_id
    )
    return jsonify(invite.to_dict()), 201


@tournament_bp.post("/invite/<uuid:invite_id>/accept")
def accept_invite(invite_id):
    try:
        coach = get_current_coach()
    except Exception as e:
        return jsonify({"error": str(e)}), 401

    result = InviteService.accept_invite(invite_id)
    return jsonify(result.to_dict()), 200


@tournament_bp.post("/invite/<uuid:invite_id>/reject")
def reject_invite(invite_id):
    try:
        coach = get_current_coach()
    except Exception as e:
        return jsonify({"error": str(e)}), 401

    result = InviteService.reject_invite(invite_id)
    return jsonify(result.to_dict()), 200


@tournament_bp.get('/invites')
def list_invites():
    try:
        coach = get_current_coach()
    except Exception as e:
        return jsonify({"error": str(e)}), 401

    from app.models.tournament_invite import TournamentInvite
    from app.models.team import Team

    incoming = TournamentInvite.query.filter_by(to_coach_id=coach.id).all()
    sent = TournamentInvite.query.filter_by(from_coach_id=coach.id).all()

    def enrich(inv):
        d = inv.to_dict()
        d['team_name'] = None
        try:
            if inv.team_id:
                t = Team.query.get(inv.team_id)
                d['team_name'] = t.name if t else None
        except Exception:
            d['team_name'] = None
        from app.models.tournament import Tournament
        try:
            t = Tournament.query.get(inv.tournament_id)
            d['tournament_name'] = t.name if t else None
        except Exception:
            d['tournament_name'] = None
        return d

    return jsonify({
        'incoming': [enrich(i) for i in incoming],
        'sent': [enrich(i) for i in sent]
    })


@tournament_bp.get("/<uuid:tournament_id>/teams")
def list_tournament_teams(tournament_id):
    try:
        teams = TournamentService.list_teams(tournament_id)
        return jsonify(teams), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
