from app.extensions.db import db
from app.models import (
    Competition, CompetitionTeam, CompetitionGroup, KnockoutRound, 
    CompetitionAdvancementRule, Match, Team
)
from sqlalchemy import func
import uuid


class CompetitionService:
    """Service for managing competitions and teams"""
    
    @staticmethod
    def create_competition(season_id, name, stage_level, format_type='knockout', 
                         legs=1, points_win=3, points_draw=1, points_loss=0,
                         region_id=None, county_id=None, max_teams=None, min_teams=2):
        """Create a new competition with specified configuration"""
        competition = Competition(
            season_id=season_id,
            name=name,
            stage_level=stage_level,
            format_type=format_type,
            legs=legs,
            points_win=points_win,
            points_draw=points_draw,
            points_loss=points_loss,
            region_id=region_id,
            county_id=county_id,
            max_teams=max_teams,
            min_teams=min_teams,
            status='draft'
        )
        db.session.add(competition)
        db.session.commit()
        return competition

    @staticmethod
    def add_teams_auto(competition_id, team_ids):
        """Auto-qualify teams to a competition"""
        competition = Competition.query.get(competition_id)
        if not competition:
            raise ValueError(f"Competition {competition_id} not found")
        
        # Check max_teams constraint
        existing_count = CompetitionTeam.query.filter_by(competition_id=competition_id).count()
        if competition.max_teams and (existing_count + len(team_ids)) > competition.max_teams:
            raise ValueError(f"Adding {len(team_ids)} teams would exceed max_teams limit of {competition.max_teams}")
        
        added_teams = []
        for i, team_id in enumerate(team_ids, start=existing_count + 1):
            # Skip if team already in competition
            existing = CompetitionTeam.query.filter_by(
                competition_id=competition_id,
                team_id=team_id
            ).first()
            if existing:
                continue
            
            comp_team = CompetitionTeam(
                competition_id=competition_id,
                team_id=team_id,
                manually_added=False,
                seeded_position=i
            )
            db.session.add(comp_team)
            added_teams.append(comp_team)
        
        db.session.commit()
        return added_teams

    @staticmethod
    def add_teams_manual(competition_id, team_ids):
        """Manually add teams to a competition (override)"""
        competition = Competition.query.get(competition_id)
        if not competition:
            raise ValueError(f"Competition {competition_id} not found")
        
        # Check max_teams constraint
        existing_count = CompetitionTeam.query.filter_by(competition_id=competition_id).count()
        if competition.max_teams and (existing_count + len(team_ids)) > competition.max_teams:
            raise ValueError(f"Adding {len(team_ids)} teams would exceed max_teams limit of {competition.max_teams}")
        
        added_teams = []
        for i, team_id in enumerate(team_ids, start=existing_count + 1):
            # Skip if team already in competition
            existing = CompetitionTeam.query.filter_by(
                competition_id=competition_id,
                team_id=team_id
            ).first()
            if existing:
                continue
            
            comp_team = CompetitionTeam(
                competition_id=competition_id,
                team_id=team_id,
                manually_added=True,
                seeded_position=i
            )
            db.session.add(comp_team)
            added_teams.append(comp_team)
        
        db.session.commit()
        return added_teams

    @staticmethod
    def get_competition_standings(competition_id):
        """Get standings for a competition based on match results and points system"""
        competition = Competition.query.get(competition_id)
        if not competition:
            raise ValueError(f"Competition {competition_id} not found")
        
        # Get all teams in competition
        comp_teams = CompetitionTeam.query.filter_by(competition_id=competition_id).all()
        
        standings = []
        for comp_team in comp_teams:
            team = Team.query.get(comp_team.team_id)
            
            # Get all matches for this team in this competition
            matches = Match.query.filter(
                Match.competition_id == competition_id,
                db.or_(
                    Match.home_team_id == comp_team.team_id,
                    Match.away_team_id == comp_team.team_id
                )
            ).all()
            
            # Calculate stats
            points = 0
            played = 0
            wins = 0
            draws = 0
            losses = 0
            goals_for = 0
            goals_against = 0
            
            for match in matches:
                # Only count completed matches
                if match.status.value not in ['finished']:
                    continue
                
                played += 1
                
                if match.home_team_id == comp_team.team_id:
                    goals_for += match.home_score
                    goals_against += match.away_score
                    
                    if match.home_score > match.away_score:
                        wins += 1
                        points += competition.points_win
                    elif match.home_score == match.away_score:
                        draws += 1
                        points += competition.points_draw
                    else:
                        losses += 1
                        points += competition.points_loss
                else:
                    goals_for += match.away_score
                    goals_against += match.home_score
                    
                    if match.away_score > match.home_score:
                        wins += 1
                        points += competition.points_win
                    elif match.away_score == match.home_score:
                        draws += 1
                        points += competition.points_draw
                    else:
                        losses += 1
                        points += competition.points_loss
            
            standing = {
                'team_id': str(comp_team.team_id),
                'team_name': team.name if team else 'Unknown',
                'played': played,
                'wins': wins,
                'draws': draws,
                'losses': losses,
                'points': points,
                'goals_for': goals_for,
                'goals_against': goals_against,
                'goal_difference': goals_for - goals_against,
                'seeded_position': comp_team.seeded_position,
            }
            standings.append(standing)
        
        # Sort by: points DESC, goal_difference DESC, goals_for DESC
        standings.sort(key=lambda x: (-x['points'], -x['goal_difference'], -x['goals_for']))
        
        return standings

    @staticmethod
    def create_advancement_rule(from_competition_id, to_competition_id=None, 
                               rule_type='top_positions', advancement_positions=None, auto_apply=True):
        """Create an advancement rule between competitions"""
        rule = CompetitionAdvancementRule(
            from_competition_id=from_competition_id,
            to_competition_id=to_competition_id,
            rule_type=rule_type,
            advancement_positions=advancement_positions,
            auto_apply=auto_apply
        )
        db.session.add(rule)
        db.session.commit()
        return rule

    @staticmethod
    def get_eligible_teams_for_advancement(from_competition_id, to_competition_id=None):
        """Get teams eligible to advance based on advancement rules"""
        from_comp = Competition.query.get(from_competition_id)
        if not from_comp:
            raise ValueError(f"Competition {from_competition_id} not found")
        
        # Get advancement rule
        rule = CompetitionAdvancementRule.query.filter_by(
            from_competition_id=from_competition_id
        ).first()
        
        if not rule:
            return []
        
        standings = CompetitionService.get_competition_standings(from_competition_id)
        eligible_teams = []
        
        if rule.rule_type == 'top_positions':
            # Return top N teams by standings
            count = rule.advancement_positions or len(standings)
            for standing in standings[:count]:
                eligible_teams.append({
                    'team_id': standing['team_id'],
                    'team_name': standing['team_name'],
                    'position': standings.index(standing) + 1,
                    'points': standing['points'],
                })
        
        elif rule.rule_type == 'group_winners':
            # Return winners from each group (for group_knockout format)
            groups = CompetitionGroup.query.filter_by(competition_id=from_competition_id).all()
            for group in groups:
                group_standings = [s for s in standings if CompetitionTeam.query.filter_by(
                    competition_id=from_competition_id,
                    team_id=s['team_id'],
                    group_id=group.id
                ).first()]
                
                if group_standings:
                    winner = group_standings[0]
                    eligible_teams.append({
                        'team_id': winner['team_id'],
                        'team_name': winner['team_name'],
                        'group': group.name,
                        'points': winner['points'],
                    })
        
        elif rule.rule_type == 'knockout_winner':
            # Only knockout winner
            if standings:
                winner = standings[0]
                eligible_teams.append({
                    'team_id': winner['team_id'],
                    'team_name': winner['team_name'],
                    'points': winner['points'],
                })
        
        return eligible_teams

    @staticmethod
    def get_competition_by_id(competition_id):
        """Get competition details with team count and status"""
        competition = Competition.query.get(competition_id)
        if not competition:
            return None
        
        team_count = CompetitionTeam.query.filter_by(competition_id=competition_id).count()
        match_count = Match.query.filter_by(competition_id=competition_id).count()
        
        return {
            **competition.to_dict(),
            'team_count': team_count,
            'match_count': match_count,
        }

    @staticmethod
    def get_competitions_by_season(season_id, stage_level=None):
        """Get all competitions for a season, optionally filtered by stage"""
        query = Competition.query.filter_by(season_id=season_id)
        
        if stage_level:
            query = query.filter_by(stage_level=stage_level)
        
        competitions = query.all()
        
        result = []
        for comp in competitions:
            team_count = CompetitionTeam.query.filter_by(competition_id=comp.id).count()
            result.append({
                **comp.to_dict(),
                'team_count': team_count,
            })
        
        return result
