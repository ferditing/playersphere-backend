from flask import Blueprint, request, jsonify
from app.models import Competition, CompetitionTeam, Team
from app.services.competition_service import CompetitionService
from app.services.scheduling_service import SchedulingService
from app.services.advancement_service import AdvancementService
from app.extensions.db import db
from functools import wraps
import uuid

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
        data = request.get_json()
        
        # Validate required fields
        required = ['season_id', 'name', 'stage_level', 'format_type']
        if not all(k in data for k in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        competition = CompetitionService.create_competition(
            season_id=uuid.UUID(data['season_id']),
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
        )
        
        return jsonify(competition.to_dict()), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@competition_bp.route('', methods=['GET'])
@require_auth
def get_competitions():
    """List competitions with optional filtering"""
    try:
        season_id = request.args.get('season_id')
        stage_level = request.args.get('stage_level')
        status = request.args.get('status')
        
        if not season_id:
            return jsonify({'error': 'season_id parameter required'}), 400
        
        competitions = CompetitionService.get_competitions_by_season(
            uuid.UUID(season_id),
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
        return jsonify({'error': str(e)}), 500


@competition_bp.route('/<competition_id>/fixtures', methods=['GET'])
@require_auth
def get_fixtures(competition_id):
    """Get all fixtures for a competition"""
    try:
        group_id = request.args.get('group_id')
        knockout_round_id = request.args.get('knockout_round_id')
        
        query_group_id = uuid.UUID(group_id) if group_id else None
        query_knockout_id = uuid.UUID(knockout_round_id) if knockout_round_id else None
        
        fixtures = SchedulingService.get_schedule(
            uuid.UUID(competition_id),
            group_id=query_group_id,
            knockout_round_id=query_knockout_id
        )
        
        return jsonify(fixtures), 200
    
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
