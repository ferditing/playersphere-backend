from flask import Blueprint, jsonify, request
from app.models.match import Match
from app.models.team_stats import TeamStats
from app.models.player_stats import PlayerStats
from app.models.player import Player
from app.models.team import Team
from app.models.county import County
from app.services.age_group_service import player_age_group
from app.services.match_service import compute_score

bp = Blueprint("public", __name__, url_prefix="/api/public")


@bp.route("/test-cors", methods=["GET", "OPTIONS"])
def test_cors():
    return jsonify({"message": "CORS is working!", "status": "success"})


@bp.get("/counties")
def public_counties():
    """Get all counties with their IDs"""
    counties = County.query.all()
    return jsonify([{"id": str(c.id), "name": c.name} for c in counties])


@bp.get("/feeds")
def feeds():
    from sqlalchemy.orm import joinedload
    from app.models.enums import MatchStatus
    
    status_filter = request.args.get('status')
    print(f"Feeds called with status_filter: {status_filter}")
    
    query = Match.query.options(
        joinedload(Match.events),
        joinedload(Match.home_team),
        joinedload(Match.away_team)
    )
    
    if status_filter:
        if status_filter == 'live':
            query = query.filter(Match.status == MatchStatus.live)
            print("Filtering for live matches")
        elif status_filter == 'scheduled':
            query = query.filter(Match.status == MatchStatus.scheduled)
            print("Filtering for scheduled matches")
        elif status_filter == 'finished':
            query = query.filter(Match.status == MatchStatus.finished)
            print("Filtering for finished matches")
    
    matches = query.order_by(Match.match_date.desc()).limit(50).all()
    print(f"Found {len(matches)} matches")
    for match in matches:
        print(f"Match {match.id}: status={match.status}, status_value={match.status.value if match.status else None}")

    result = []
    for match in matches:
        # Use stored scores instead of recalculating from events
        # The scores are already updated when events are created
        result.append(match.to_dict())

    return jsonify(result)


@bp.get("/teams")
def public_teams():
    q = request.args.get('q')
    if q:
        # case-insensitive name search
        teams = Team.query.filter(Team.name.ilike(f"%{q}%")).limit(20).all()
    else:
        teams = Team.query.all()
    return jsonify([t.to_dict() for t in teams])


@bp.get("/team-stats")
def all_team_stats():
    stats = TeamStats.query.all()
    return jsonify([s.to_dict() for s in stats])


@bp.get("/player-stats")
def all_player_stats():
    stats = PlayerStats.query.all()
    return jsonify([s.to_dict() for s in stats])


@bp.get("/team-stats/<uuid:team_id>")
def team_stats(team_id):
    stats = TeamStats.query.filter_by(team_id=team_id).all()
    return jsonify([s.to_dict() for s in stats])


@bp.get("/player-stats/<uuid:player_id>")
def player_stats(player_id):
    stats = PlayerStats.query.filter_by(player_id=player_id).all()
    return jsonify([s.to_dict() for s in stats])


@bp.get("/players")
def public_players():
    from sqlalchemy.orm import joinedload
    age_group = request.args.get("age_group")  # U15 / U17 / SENIOR

    players = Player.query.options(joinedload(Player.team)).all()
    if age_group:
        players = [p for p in players if player_age_group(p) == age_group]

    return jsonify([
        {
            **p.to_dict(),
            "age_group": player_age_group(p)
        }
        for p in players
    ])


@bp.get("/teams/<uuid:team_id>/players")
def public_team_players(team_id):
    team = Team.query.get_or_404(team_id)
    players = team.players
    return jsonify([
        {
            **p.to_dict(),
            "age_group": player_age_group(p)
        }
        for p in players
    ])


@bp.get("/admin-competitions", strict_slashes=False)
def public_admin_competitions():
    """Get all admin-created competitions (public view)"""
    try:
        from app.models.competition import Competition
        
        status_filter = request.args.get('status')
        stage_filter = request.args.get('stage_level')
        
        query = Competition.query.filter(Competition.created_by.isnot(None))
        
        if status_filter:
            query = query.filter(Competition.status == status_filter)
        # Note: We now show ALL competitions (including draft) for admin-created ones
        # They can be filtered by status param if needed
        
        if stage_filter:
            query = query.filter(Competition.stage_level == stage_filter)
        
        competitions = query.order_by(Competition.created_at.desc()).all()
        return jsonify([c.to_dict() for c in competitions]), 200
    except Exception as e:
        import traceback
        print(f"Error fetching admin competitions: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
