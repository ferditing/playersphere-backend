from flask import Blueprint, request, jsonify
from app.models import Competition, CompetitionTeam, Team, KnockoutRound, Match, CompetitionGroup
from app.services.competition_service import CompetitionService
from app.services.scheduling_service import SchedulingService
from app.services.advancement_service import AdvancementService
from app.services.auth_service import get_current_user
from app.extensions.db import db
from functools import wraps
import uuid
from datetime import datetime, timedelta

competition_bp = Blueprint('competitions', __name__, url_prefix='/api/competitions')


def require_auth(f):
    """Placeholder for authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TODO: Implement actual auth check
        return f(*args, **kwargs)
    return decorated_function


def require_admin(f):
    """Placeholder for admin authorization"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TODO: Implement actual admin check
        return f(*args, **kwargs)
    return decorated_function


# ============================================================
# COMPETITION CRUD ROUTES
# ============================================================

@competition_bp.route('', methods=['POST'])
@require_admin
def create_competition():
    """Create a new competition"""
    try:
        # Log request headers
        auth_header = request.headers.get('Authorization')
        print(f"DEBUG: Authorization header present: {bool(auth_header)}")
        if auth_header:
            print(f"DEBUG: Auth header value: {auth_header[:20]}..." if len(auth_header) > 20 else f"DEBUG: Auth header value: {auth_header}")
        
        # Get current admin
        admin_id = None
        try:
            user = get_current_user()
            admin_id = user.id if hasattr(user, 'id') else None
            print(f"DEBUG: Auth successful, admin_id={admin_id}, user type={type(user).__name__}")
        except Exception as auth_err:
            print(f"DEBUG: Auth failed with error: {auth_err}")
            admin_id = None
        
        data = request.get_json()
        print(f"DEBUG: Creating competition with created_by={admin_id}")
        
        # Validate required fields
        required = ['season_id', 'name', 'stage_level', 'format_type']
        if not all(k in data for k in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Handle season_id - convert string/year to UUID if needed
        season_str = data['season_id']
        if isinstance(season_str, str) and '-' not in season_str:
            # If it's a year string like "2026", generate a deterministic UUID
            season_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"season-{season_str}")
        else:
            # Otherwise treat it as a UUID string
            season_id = uuid.UUID(season_str)
        
        competition = CompetitionService.create_competition(
            season_id=season_id,
            name=data['name'],
            stage_level=data['stage_level'],
            format_type=data.get('format_type', 'knockout'),
            legs=data.get('legs', 1),
            points_win=data.get('points_win', 3),
            points_draw=data.get('points_draw', 1),
            points_loss=data.get('points_loss', 0),
            region_id=uuid.UUID(data['region_id']) if data.get('region_id') else None,
            county_id=uuid.UUID(data['county_id']) if data.get('county_id') else None,
            max_teams=data.get('max_teams'),
            min_teams=data.get('min_teams', 2),
            created_by=admin_id,
        )
        
        print(f"DEBUG: Competition created with id={competition.id}, created_by={competition.created_by}")
        return jsonify(competition.to_dict()), 201
    
    except Exception as e:
        print(f"DEBUG: Exception in create_competition: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@competition_bp.route('', methods=['GET'])
@require_auth
def get_competitions():
    """List competitions with optional filtering"""
    try:
        season_id = request.args.get('season_id')
        stage_level = request.args.get('stage_level')
        status = request.args.get('status')
        
        # If season_id not provided, use current year
        if not season_id:
            from datetime import datetime
            season_id = str(datetime.utcnow().year)
        
        # Handle season_id - convert string/year to UUID if needed
        if isinstance(season_id, str) and '-' not in season_id:
            # If it's a year string like "2026", generate a deterministic UUID
            season_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, f"season-{season_id}")
        else:
            # Otherwise treat it as a UUID string
            season_uuid = uuid.UUID(season_id)
        
        competitions = CompetitionService.get_competitions_by_season(
            season_uuid,
            stage_level=stage_level
        )
        
        # Filter by status if provided
        if status:
            competitions = [c for c in competitions if c['status'] == status]
        
        return jsonify(competitions), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@competition_bp.route('/<competition_id>', methods=['GET'])
@require_auth
def get_competition(competition_id):
    """Get competition details with standings and stats"""
    try:
        competition = CompetitionService.get_competition_by_id(uuid.UUID(competition_id))
        
        if not competition:
            return jsonify({'error': 'Competition not found'}), 404
        
        # Get standings
        standings = CompetitionService.get_competition_standings(uuid.UUID(competition_id))
        
        return jsonify({
            'competition': competition,
            'standings': standings,
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@competition_bp.route('/<competition_id>', methods=['PATCH'])
@require_admin
def update_competition(competition_id):
    """Update competition configuration"""
    try:
        competition = Competition.query.get(uuid.UUID(competition_id))
        
        if not competition:
            return jsonify({'error': 'Competition not found'}), 404
        
        data = request.get_json()
        
        # Allow updating certain fields
        updateable_fields = ['name', 'status', 'max_teams', 'min_teams', 
                           'points_win', 'points_draw', 'points_loss']
        
        for field in updateable_fields:
            if field in data:
                setattr(competition, field, data[field])
        
        db.session.commit()
        
        return jsonify(competition.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@competition_bp.route('/<competition_id>', methods=['DELETE'])
@require_admin
def delete_competition(competition_id):
    """Delete a competition and all associated data"""
    try:
        competition = Competition.query.get(uuid.UUID(competition_id))
        
        if not competition:
            return jsonify({'error': 'Competition not found'}), 404
        
        # Delete all matches associated with this competition
        from app.models.match import Match
        from app.models.match_event import MatchEvent
        
        matches = Match.query.filter_by(competition_id=uuid.UUID(competition_id)).all()
        for match in matches:
            MatchEvent.query.filter_by(match_id=match.id).delete()
            db.session.delete(match)
        
        # The cascade delete in the model will handle:
        # - competition_teams
        # - groups
        # - knockout_rounds
        # - advancement_rules
        
        db.session.delete(competition)
        db.session.commit()
        
        return jsonify({'message': f'Competition "{competition.name}" deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================
# TEAM MANAGEMENT ROUTES
# ============================================================

@competition_bp.route('/<competition_id>/teams', methods=['POST'])
@require_admin
def add_teams_auto(competition_id):
    """Auto-qualify teams to competition"""
    try:
        data = request.get_json()
        
        if 'team_ids' not in data or not isinstance(data['team_ids'], list):
            return jsonify({'error': 'team_ids array required'}), 400
        
        team_ids = [uuid.UUID(tid) if isinstance(tid, str) else tid for tid in data['team_ids']]
        
        # Verify teams exist
        for tid in team_ids:
            team = Team.query.get(tid)
            if not team:
                return jsonify({'error': f'Team {tid} not found'}), 404
        
        added = CompetitionService.add_teams_auto(uuid.UUID(competition_id), team_ids)
        
        return jsonify({
            'added_count': len(added),
            'teams': [{'id': str(t.id), 'team_id': str(t.team_id)} for t in added]
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@competition_bp.route('/<competition_id>/teams/manual', methods=['POST'])
@require_admin
def add_teams_manual(competition_id):
    """Manually add teams to competition (override)"""
    try:
        data = request.get_json()
        
        if 'team_ids' not in data or not isinstance(data['team_ids'], list):
            return jsonify({'error': 'team_ids array required'}), 400
        
        team_ids = [uuid.UUID(tid) if isinstance(tid, str) else tid for tid in data['team_ids']]
        
        # Verify teams exist
        for tid in team_ids:
            team = Team.query.get(tid)
            if not team:
                return jsonify({'error': f'Team {tid} not found'}), 404
        
        added = CompetitionService.add_teams_manual(uuid.UUID(competition_id), team_ids)
        
        return jsonify({
            'added_count': len(added),
            'teams': [{'id': str(t.id), 'team_id': str(t.team_id), 'manually_added': True} for t in added]
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@competition_bp.route('/<competition_id>/teams', methods=['GET'])
@require_auth
def get_competition_teams(competition_id):
    """Get all teams in a competition"""
    try:
        comp_teams = CompetitionTeam.query.filter_by(
            competition_id=uuid.UUID(competition_id)
        ).all()
        
        teams_data = []
        for ct in comp_teams:
            team = Team.query.get(ct.team_id)
            teams_data.append({
                'id': str(ct.id),
                'team_id': str(ct.team_id),
                'team_name': team.name if team else 'Unknown',
                'manually_added': ct.manually_added,
                'seeded_position': ct.seeded_position,
                'group_id': str(ct.group_id) if ct.group_id else None,
            })
        
        return jsonify(teams_data), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# FIXTURES/SCHEDULE ROUTES
# ============================================================

@competition_bp.route('/<competition_id>/fixtures', methods=['GET'])
@require_auth
def get_competition_fixtures(competition_id):
    """Get all fixtures/matches for a competition"""
    try:
        from app.models.match import Match
        from sqlalchemy.orm import joinedload
        
        # Get all matches for this competition
        matches = Match.query.options(
            joinedload(Match.home_team),
            joinedload(Match.away_team)
        ).filter_by(
            competition_id=uuid.UUID(competition_id)
        ).order_by(
            Match.match_date
        ).all()
        
        # Convert to dict format
        fixtures = []
        for match in matches:
            fixtures.append(match.to_dict())
        
        return jsonify(fixtures), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@competition_bp.route('/<competition_id>/matches', methods=['GET'])
@require_auth
def get_competition_matches(competition_id):
    """Get all matches for a competition (alias for fixtures)"""
    try:
        from app.models.match import Match
        from sqlalchemy.orm import joinedload
        
        # Get all matches for this competition, ordered by date
        matches = Match.query.options(
            joinedload(Match.home_team),
            joinedload(Match.away_team)
        ).filter_by(
            competition_id=uuid.UUID(competition_id)
        ).order_by(
            Match.match_date
        ).all()
        
        # Convert to dict format
        return jsonify([m.to_dict() for m in matches]), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@competition_bp.route('/<competition_id>/generate-fixtures', methods=['POST'])
@require_admin
def generate_fixtures(competition_id):
    """Generate fixtures based on competition format"""
    try:
        competition = Competition.query.get(uuid.UUID(competition_id))
        
        if not competition:
            return jsonify({'error': 'Competition not found'}), 404
        
        data = request.get_json() or {}
        start_date = data.get('start_date')
        days_between = data.get('days_between_matches', 7)
        
        matches = []
        
        if competition.format_type == 'round_robin':
            matches = SchedulingService.generate_round_robin_fixtures(
                uuid.UUID(competition_id),
                days_between_matches=days_between
            )
        
        elif competition.format_type == 'knockout':
            matches = SchedulingService.generate_knockout_brackets(
                uuid.UUID(competition_id),
                days_between_rounds=days_between
            )
        
        elif competition.format_type == 'group_knockout':
            num_groups = data.get('num_groups', 4)
            matches = SchedulingService.generate_group_knockout_fixtures(
                uuid.UUID(competition_id),
                groups_config=num_groups,
                days_between_matches=days_between
            )
        
        return jsonify({
            'generated_matches': len(matches),
            'format_type': competition.format_type,
            'matches': [m.to_dict() for m in matches[:5]]  # Sample first 5
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        import traceback
        print(f"Exception in generate_fixtures: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@competition_bp.route('/<competition_id>/generate-knockout-fixtures', methods=['POST'])
@require_admin
def generate_knockout_fixtures(competition_id):
    """Generate knockout fixtures for qualified teams"""
    try:
        competition = Competition.query.get(uuid.UUID(competition_id))
        
        if not competition:
            return jsonify({'error': 'Competition not found'}), 404
        
        # Get qualified teams from standings (top teams)
        standings = CompetitionService.get_competition_standings(uuid.UUID(competition_id))
        qualified_teams = [s['team_id'] for s in standings[:16]]  # Top 16 or adjust
        
        if len(qualified_teams) < 2:
            return jsonify({'error': 'Not enough qualified teams for knockout'}), 400
        
        data = request.get_json() or {}
        start_date = data.get('start_date')
        
        matches = SchedulingService.generate_knockout_from_teams(
            uuid.UUID(competition_id),
            qualified_teams,
            start_date=start_date
        )
        
        return jsonify({
            'generated_matches': len(matches),
            'qualified_teams': len(qualified_teams),
            'matches': [m.to_dict() for m in matches[:5]]
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        import traceback
        print(f"Exception in generate_knockout_fixtures: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# STANDINGS ROUTES
# ============================================================

@competition_bp.route('/<competition_id>/standings', methods=['GET'])
@require_auth
def get_standings(competition_id):
    """Get current standings for competition"""
    try:
        standings = CompetitionService.get_competition_standings(uuid.UUID(competition_id))
        
        return jsonify(standings), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# ADVANCEMENT/QUALIFICATION ROUTES
# ============================================================

@competition_bp.route('/<from_id>/to/<to_id>/eligible-teams', methods=['GET'])
@require_auth
def get_eligible_teams(from_id, to_id):
    """Get teams eligible to advance from one competition to another"""
    try:
        eligible = CompetitionService.get_eligible_teams_for_advancement(
            uuid.UUID(from_id),
            uuid.UUID(to_id)
        )
        
        return jsonify(eligible), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@competition_bp.route('/<from_id>/advance-to/<to_id>', methods=['POST'])
@require_admin
def advance_teams(from_id, to_id):
    """Auto-advance teams by standings"""
    try:
        data = request.get_json() or {}
        num_positions = data.get('num_positions')
        
        result = AdvancementService.advance_teams_by_standings(
            uuid.UUID(from_id),
            uuid.UUID(to_id),
            num_positions=num_positions
        )
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@competition_bp.route('/<from_id>/advance-manual/<to_id>', methods=['POST'])
@require_admin
def advance_teams_manual(from_id, to_id):
    """Manually advance specific teams"""
    try:
        data = request.get_json()
        
        if 'team_ids' not in data or not isinstance(data['team_ids'], list):
            return jsonify({'error': 'team_ids array required'}), 400
        
        result = AdvancementService.advance_teams_manually(
            uuid.UUID(from_id),
            uuid.UUID(to_id),
            data['team_ids']
        )
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@competition_bp.route('/<competition_id>/apply-rules', methods=['POST'])
@require_admin
def apply_advancement_rules(competition_id):
    """Apply all advancement rules for a competition"""
    try:
        results = AdvancementService.apply_advancement_rules(uuid.UUID(competition_id))
        
        return jsonify({
            'total_rules': len(results),
            'results': results
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# GROUP MANAGEMENT ROUTES
# ============================================================

@competition_bp.route('/<competition_id>/groups', methods=['POST'])
@require_admin
def create_group(competition_id):
    """Create a new group for a competition"""
    try:
        data = request.get_json()
        
        if 'name' not in data:
            return jsonify({'error': 'Group name required'}), 400
        
        competition = Competition.query.get(uuid.UUID(competition_id))
        if not competition:
            return jsonify({'error': 'Competition not found'}), 404
        
        # Check if group name already exists for this competition
        existing = CompetitionGroup.query.filter_by(
            competition_id=uuid.UUID(competition_id),
            name=data['name']
        ).first()
        
        if existing:
            return jsonify({'error': f'Group "{data["name"]}" already exists'}), 400
        
        group = CompetitionGroup(
            competition_id=uuid.UUID(competition_id),
            name=data['name'],
            group_order=data.get('group_order')
        )
        
        db.session.add(group)
        db.session.commit()
        
        return jsonify(group.to_dict()), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@competition_bp.route('/<competition_id>/groups', methods=['GET'])
@require_auth
def get_competition_groups(competition_id):
    """Get all groups for a competition"""
    try:
        groups = CompetitionGroup.query.filter_by(
            competition_id=uuid.UUID(competition_id)
        ).order_by(CompetitionGroup.group_order).all()
        
        return jsonify([group.to_dict() for group in groups]), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@competition_bp.route('/<competition_id>/groups/<group_id>/teams', methods=['POST'])
@require_admin
def assign_teams_to_group(competition_id, group_id):
    """Assign teams to a group"""
    try:
        data = request.get_json()
        
        if 'team_ids' not in data or not isinstance(data['team_ids'], list):
            return jsonify({'error': 'team_ids array required'}), 400
        
        group = CompetitionGroup.query.get(uuid.UUID(group_id))
        if not group:
            return jsonify({'error': 'Group not found'}), 404
        
        if str(group.competition_id) != competition_id:
            return jsonify({'error': 'Group does not belong to this competition'}), 400
        
        team_ids = [uuid.UUID(tid) if isinstance(tid, str) else tid for tid in data['team_ids']]
        
        # Update team assignments
        updated_count = 0
        for team_id in team_ids:
            comp_team = CompetitionTeam.query.filter_by(
                competition_id=uuid.UUID(competition_id),
                team_id=team_id
            ).first()
            
            if comp_team:
                comp_team.group_id = uuid.UUID(group_id)
                updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'updated_teams': updated_count,
            'group_id': group_id
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@competition_bp.route('/<competition_id>/groups/<group_id>/fixtures', methods=['POST'])
@require_admin
def create_group_fixture(competition_id, group_id):
    """Create a manual fixture within a group"""
    try:
        data = request.get_json()
        
        required = ['home_team_id', 'away_team_id', 'match_date']
        if not all(k in data for k in required):
            return jsonify({'error': 'home_team_id, away_team_id, and match_date required'}), 400
        
        group = CompetitionGroup.query.get(uuid.UUID(group_id))
        if not group:
            return jsonify({'error': 'Group not found'}), 404
        
        if str(group.competition_id) != competition_id:
            return jsonify({'error': 'Group does not belong to this competition'}), 400
        
        # Verify teams are in the group
        home_team = CompetitionTeam.query.filter_by(
            competition_id=uuid.UUID(competition_id),
            team_id=uuid.UUID(data['home_team_id']),
            group_id=uuid.UUID(group_id)
        ).first()
        
        away_team = CompetitionTeam.query.filter_by(
            competition_id=uuid.UUID(competition_id),
            team_id=uuid.UUID(data['away_team_id']),
            group_id=uuid.UUID(group_id)
        ).first()
        
        if not home_team or not away_team:
            return jsonify({'error': 'Both teams must be in the specified group'}), 400
        
        from app.models.match import Match
        from app.models.enums import MatchStatus
        
        match = Match(
            home_team_id=uuid.UUID(data['home_team_id']),
            away_team_id=uuid.UUID(data['away_team_id']),
            competition_id=uuid.UUID(competition_id),
            group_id=uuid.UUID(group_id),
            match_date=datetime.fromisoformat(data['match_date'].replace('Z', '+00:00')),
            status=MatchStatus.scheduled,
            country='Kenya'
        )
        
        db.session.add(match)
        db.session.commit()
        
        return jsonify(match.to_dict()), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@competition_bp.route('/<competition_id>/groups/<group_id>/fixtures', methods=['GET'])
@require_auth
def get_group_fixtures(competition_id, group_id):
    """Get all fixtures for a specific group"""
    try:
        from app.models.match import Match
        from sqlalchemy.orm import joinedload
        
        matches = Match.query.options(
            joinedload(Match.home_team),
            joinedload(Match.away_team)
        ).filter_by(
            competition_id=uuid.UUID(competition_id),
            group_id=uuid.UUID(group_id)
        ).order_by(Match.match_date).all()
        
        return jsonify([match.to_dict() for match in matches]), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@competition_bp.route('/<from_id>/advancement-summary', methods=['GET'])
@require_auth
def get_advancement_summary(from_id):
    """Get advancement summary and eligible teams"""
    try:
        to_id = request.args.get('to_id')
        to_uuid = uuid.UUID(to_id) if to_id else None
        
        summary = AdvancementService.get_advancement_summary(
            uuid.UUID(from_id),
            to_competition_id=to_uuid
        )
        
        return jsonify(summary), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# KNOCKOUT BRACKET ROUTES
# ============================================================

@competition_bp.route('/<competition_id>/knockout-bracket', methods=['GET'])
@require_auth
def get_knockout_bracket(competition_id):
    """Get the complete knockout bracket structure for visualization"""
    try:
        bracket = SchedulingService.get_knockout_bracket(uuid.UUID(competition_id))
        return jsonify(bracket), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@competition_bp.route('/<competition_id>/knockout-rounds/<int:round_order>/next', methods=['POST'])
@require_admin
def generate_next_knockout_round(competition_id, round_order):
    """
    Auto-generate the next knockout round based on winners of the current round.
    Call this after all matches in a round are completed.
    """
    try:
        matches = SchedulingService.generate_next_knockout_round(
            uuid.UUID(competition_id),
            round_order
        )
        
        if matches is None:
            return jsonify({'message': 'Tournament is complete'}), 200
        
        return jsonify({
            'generated_matches': len(matches),
            'matches': [m.to_dict() for m in matches]
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}),500


@competition_bp.route('/<competition_id>/knockout-rounds/<round_id>/match-dates', methods=['PATCH'])
@require_admin
def update_knockout_round_dates(competition_id, round_id):
    """Update match dates for all matches in a knockout round"""
    try:
        data = request.get_json()
        
        start_date = data.get('start_date')
        days_between = data.get('days_between_matches', 7)
        
        if not start_date:
            return jsonify({'error': 'start_date is required'}), 400
        
        # Parse the date
        from datetime import datetime
        start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        
        # Get all matches in this round
        ko_round = KnockoutRound.query.get(uuid.UUID(round_id))
        if not ko_round:
            return jsonify({'error': 'Round not found'}), 404
        
        if str(ko_round.competition_id) != competition_id:
            return jsonify({'error': 'Round does not belong to this competition'}), 400
        
        matches = Match.query.filter_by(knockout_round_id=uuid.UUID(round_id)).order_by(
            Match.match_date
        ).all()
        
        if not matches:
            return jsonify({'error': 'No matches found in this round'}), 404
        
        # Update match dates
        current_date = start_datetime
        for match in matches:
            match.match_date = current_date
            current_date += timedelta(days=days_between)
        
        db.session.commit()
        
        return jsonify({
            'updated_count': len(matches),
            'matches': [m.to_dict() for m in matches]
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
