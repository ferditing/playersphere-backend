from app.extensions.db import db
from app.models import (
    Competition, CompetitionTeam, CompetitionAdvancementRule
)
from app.services.competition_service import CompetitionService
import uuid


class AdvancementService:
    """Service for managing team advancement between competitions/tiers"""
    
    @staticmethod
    def advance_teams_by_standings(from_competition_id, to_competition_id, num_positions=None):
        """Auto-advance top N teams from standings to next competition"""
        from_comp = Competition.query.get(from_competition_id)
        to_comp = Competition.query.get(to_competition_id)
        
        if not from_comp or not to_comp:
            raise ValueError("One or both competitions not found")
        
        # Get standings
        standings = CompetitionService.get_competition_standings(from_competition_id)
        
        # Determine how many teams to advance
        if num_positions is None:
            # Check advancement rule
            rule = CompetitionAdvancementRule.query.filter_by(
                from_competition_id=from_competition_id,
                to_competition_id=to_competition_id
            ).first()
            
            if rule and rule.advancement_positions:
                num_positions = rule.advancement_positions
            else:
                # Default: advance all teams
                num_positions = len(standings)
        
        # Add top N teams to destination competition
        team_ids = [s['team_id'] for s in standings[:num_positions]]
        
        # Convert string UUIDs back to actual UUIDs if needed
        team_ids = [uuid.UUID(tid) if isinstance(tid, str) else tid for tid in team_ids]
        
        advanced_teams = CompetitionService.add_teams_auto(to_competition_id, team_ids)
        
        return {
            'advanced_count': len(advanced_teams),
            'teams': [{'team_id': str(t.team_id)} for t in advanced_teams],
        }

    @staticmethod
    def advance_group_winners(from_competition_id, to_competition_id):
        """Advance winners from each group in a group-stage competition"""
        from_comp = Competition.query.get(from_competition_id)
        to_comp = Competition.query.get(to_competition_id)
        
        if not from_comp or not to_comp:
            raise ValueError("One or both competitions not found")
        
        if from_comp.format_type != 'group_knockout':
            raise ValueError("Source competition must be group_knockout format")
        
        # Get standings
        standings = CompetitionService.get_competition_standings(from_competition_id)
        
        # Get eligible teams (group winners) using the service
        eligible = CompetitionService.get_eligible_teams_for_advancement(
            from_competition_id, to_competition_id
        )
        
        team_ids = [uuid.UUID(e['team_id']) if isinstance(e['team_id'], str) else e['team_id'] 
                   for e in eligible]
        
        advanced_teams = CompetitionService.add_teams_auto(to_competition_id, team_ids)
        
        return {
            'advanced_count': len(advanced_teams),
            'teams': [{'team_id': str(t.team_id)} for t in advanced_teams],
        }

    @staticmethod
    def advance_knockout_winner(from_competition_id, to_competition_id):
        """Advance knockout winner to next competition"""
        from_comp = Competition.query.get(from_competition_id)
        to_comp = Competition.query.get(to_competition_id)
        
        if not from_comp or not to_comp:
            raise ValueError("One or both competitions not found")
        
        if from_comp.format_type not in ['knockout', 'group_knockout']:
            raise ValueError("Source competition must be knockout-based")
        
        # Get standings
        standings = CompetitionService.get_competition_standings(from_competition_id)
        
        if not standings:
            raise ValueError("No standings available")
        
        # Winner is first in standings
        winner_team_id = standings[0]['team_id']
        winner_team_id = uuid.UUID(winner_team_id) if isinstance(winner_team_id, str) else winner_team_id
        
        advanced_teams = CompetitionService.add_teams_auto(to_competition_id, [winner_team_id])
        
        return {
            'advanced_count': 1,
            'winner_team_id': str(winner_team_id),
        }

    @staticmethod
    def apply_advancement_rules(from_competition_id):
        """Apply all advancement rules defined for a competition"""
        rules = CompetitionAdvancementRule.query.filter_by(
            from_competition_id=from_competition_id,
            auto_apply=True
        ).all()
        
        results = []
        
        for rule in rules:
            if not rule.to_competition_id:
                continue
            
            try:
                if rule.rule_type == 'top_positions':
                    result = AdvancementService.advance_teams_by_standings(
                        from_competition_id,
                        rule.to_competition_id,
                        rule.advancement_positions
                    )
                    results.append({
                        'rule_id': str(rule.id),
                        'rule_type': rule.rule_type,
                        'status': 'success',
                        'result': result,
                    })
                
                elif rule.rule_type == 'group_winners':
                    result = AdvancementService.advance_group_winners(
                        from_competition_id,
                        rule.to_competition_id
                    )
                    results.append({
                        'rule_id': str(rule.id),
                        'rule_type': rule.rule_type,
                        'status': 'success',
                        'result': result,
                    })
                
                elif rule.rule_type == 'knockout_winner':
                    result = AdvancementService.advance_knockout_winner(
                        from_competition_id,
                        rule.to_competition_id
                    )
                    results.append({
                        'rule_id': str(rule.id),
                        'rule_type': rule.rule_type,
                        'status': 'success',
                        'result': result,
                    })
                
                elif rule.rule_type == 'manual_only':
                    results.append({
                        'rule_id': str(rule.id),
                        'rule_type': rule.rule_type,
                        'status': 'skipped',
                        'message': 'Manual advancement required',
                    })
                
            except Exception as e:
                results.append({
                    'rule_id': str(rule.id),
                    'rule_type': rule.rule_type,
                    'status': 'error',
                    'message': str(e),
                })
        
        return results

    @staticmethod
    def advance_teams_manually(from_competition_id, to_competition_id, team_ids):
        """Manually advance specific teams (override automatic rules)"""
        to_comp = Competition.query.get(to_competition_id)
        
        if not to_comp:
            raise ValueError(f"Competition {to_competition_id} not found")
        
        # Convert to UUIDs if needed
        team_ids = [uuid.UUID(tid) if isinstance(tid, str) else tid for tid in team_ids]
        
        # Add teams with manually_added flag
        advanced_teams = CompetitionService.add_teams_manual(to_competition_id, team_ids)
        
        return {
            'advanced_count': len(advanced_teams),
            'teams': [{'team_id': str(t.team_id)} for t in advanced_teams],
            'note': 'Teams added via manual override',
        }

    @staticmethod
    def get_advancement_summary(from_competition_id, to_competition_id=None):
        """Get summary of teams advanced from one competition"""
        from_comp = Competition.query.get(from_competition_id)
        
        if not from_comp:
            raise ValueError(f"Competition {from_competition_id} not found")
        
        rules = CompetitionAdvancementRule.query.filter_by(
            from_competition_id=from_competition_id
        ).all()
        
        summary = {
            'from_competition': {
                'id': str(from_comp.id),
                'name': from_comp.name,
                'stage_level': from_comp.stage_level,
                'format_type': from_comp.format_type,
            },
            'advancement_rules': [],
        }
        
        for rule in rules:
            if to_competition_id and rule.to_competition_id != to_competition_id:
                continue
            
            rule_summary = {
                'rule_id': str(rule.id),
                'rule_type': rule.rule_type,
                'advancement_positions': rule.advancement_positions,
                'auto_apply': rule.auto_apply,
                'to_competition_id': str(rule.to_competition_id) if rule.to_competition_id else None,
            }
            
            # Get eligible teams if rule has a destination
            if rule.to_competition_id:
                try:
                    eligible = CompetitionService.get_eligible_teams_for_advancement(
                        from_competition_id,
                        rule.to_competition_id
                    )
                    rule_summary['eligible_teams_count'] = len(eligible)
                    rule_summary['eligible_teams'] = eligible[:10]  # Limit to first 10 for summary
                except Exception as e:
                    rule_summary['error'] = str(e)
            
            summary['advancement_rules'].append(rule_summary)
        
        return summary
