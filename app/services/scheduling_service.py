from app.extensions.db import db
from app.models import (
    Competition, CompetitionTeam, CompetitionGroup, KnockoutRound, Match
)
from app.models.enums import MatchStatus
from datetime import datetime, timedelta
import random
import uuid


class SchedulingService:
    """Service for generating fixtures/schedules for competitions"""
    
    @staticmethod
    def generate_round_robin_fixtures(competition_id, start_date=None, days_between_matches=7):
        """Generate round-robin fixtures for all teams"""
        competition = Competition.query.get(competition_id)
        if not competition:
            raise ValueError(f"Competition {competition_id} not found")
        
        # Get all teams
        comp_teams = CompetitionTeam.query.filter_by(competition_id=competition_id).all()
        team_ids = [ct.team_id for ct in comp_teams]
        
        if len(team_ids) < 2:
            raise ValueError("Need at least 2 teams for round-robin")
        
        if start_date is None:
            start_date = datetime.utcnow()
        
        matches = []
        match_date = start_date
        
        # Generate fixtures for each leg
        for leg in range(competition.legs):
            # Generate all pairings
            pairings = SchedulingService._generate_pairings(team_ids)
            
            for home_id, away_id in pairings:
                match = Match(
                    home_team_id=home_id,
                    away_team_id=away_id,
                    competition_id=competition_id,
                    match_date=match_date,
                    status=MatchStatus.scheduled,
                    country='Kenya'  # Default
                )
                db.session.add(match)
                matches.append(match)
                
                # Space out matches
                match_date += timedelta(days=days_between_matches)
        
        db.session.commit()
        return matches

    @staticmethod
    def generate_knockout_brackets(competition_id, start_date=None, days_between_rounds=14):
        """Generate knockout bracket structure"""
        competition = Competition.query.get(competition_id)
        if not competition:
            raise ValueError(f"Competition {competition_id} not found")
        
        comp_teams = CompetitionTeam.query.filter_by(competition_id=competition_id).all()
        team_ids = [ct.team_id for ct in comp_teams]
        
        if len(team_ids) < 2:
            raise ValueError("Need at least 2 teams for knockout")
        
        if start_date is None:
            start_date = datetime.utcnow()
        
        # Shuffle for random bracket assignment
        random.shuffle(team_ids)
        
        # Determine bracket structure
        rounds = SchedulingService._determine_knockout_rounds(len(team_ids))
        
        matches = []
        match_date = start_date
        
        # Only generate the first round initially
        round_name = rounds[0] if rounds else "First Round"
        
        # Create the knockout round
        ko_round = KnockoutRound(
            competition_id=competition_id,
            round_name=round_name,
            round_order=1,
            matches_per_pairing=competition.legs,
            status='active'  # Mark as active for current play
        )
        db.session.add(ko_round)
        db.session.flush()  # Get the ID
        
        # Pair teams in this round
        pairings = [(team_ids[i], team_ids[i+1]) 
                   for i in range(0, len(team_ids) - 1, 2)]
        
        for home_id, away_id in pairings:
            match = Match(
                home_team_id=home_id,
                away_team_id=away_id,
                competition_id=competition_id,
                knockout_round_id=ko_round.id,
                match_date=match_date,
                status=MatchStatus.scheduled,
                country='Kenya'
            )
            db.session.add(match)
            matches.append(match)
            match_date += timedelta(days=days_between_rounds)
        
        # Note: Subsequent rounds will be generated after this round's results are posted
        # The remaining teams logic is not used here since we only do first round
        
        db.session.commit()
        return matches

    @staticmethod
    def generate_group_knockout_fixtures(competition_id, groups_config=None, 
                                        start_date=None, days_between_matches=7):
        """Generate group stage + knockout fixtures"""
        competition = Competition.query.get(competition_id)
        if not competition:
            raise ValueError(f"Competition {competition_id} not found")
        
        comp_teams = CompetitionTeam.query.filter_by(competition_id=competition_id).all()
        team_ids = [ct.team_id for ct in comp_teams]
        
        if len(team_ids) < 4:
            raise ValueError("Need at least 4 teams for group knockout")
        
        if start_date is None:
            start_date = datetime.utcnow()
        
        # Default: 4 groups if not specified
        num_groups = groups_config or 4
        teams_per_group = len(team_ids) // num_groups
        
        if teams_per_group < 2:
            raise ValueError(f"Cannot divide {len(team_ids)} teams into {num_groups} groups with at least 2 teams each")
        
        matches = []
        match_date = start_date
        
        # Shuffle and divide into groups
        random.shuffle(team_ids)
        
        # Create groups and assign teams
        for group_idx in range(num_groups):
            group = CompetitionGroup(
                competition_id=competition_id,
                name=f"Group {chr(65 + group_idx)}",  # Group A, B, C, D, etc.
                group_order=group_idx + 1
            )
            db.session.add(group)
            db.session.flush()
            
            # Get teams for this group
            start_idx = group_idx * teams_per_group
            end_idx = start_idx + teams_per_group
            group_team_ids = team_ids[start_idx:end_idx]
            
            # Assign teams to group
            for comp_team in comp_teams:
                if comp_team.team_id in group_team_ids:
                    comp_team.group_id = group.id
            
            # Generate round-robin within group
            pairings = SchedulingService._generate_pairings(group_team_ids)
            
            for home_id, away_id in pairings:
                match = Match(
                    home_team_id=home_id,
                    away_team_id=away_id,
                    competition_id=competition_id,
                    group_id=group.id,
                    match_date=match_date,
                    status=MatchStatus.scheduled,
                    country='Kenya'
                )
                db.session.add(match)
                matches.append(match)
                match_date += timedelta(days=days_between_matches)
        
        # After group stage, knockout fixtures will be generated separately
        # ko_round = KnockoutRound(
        #     competition_id=competition_id,
        #     round_name="Knockout",
        #     round_order=num_groups + 1,
        #     matches_per_pairing=competition.legs,
        #     status='pending'
        # )
        # db.session.add(ko_round)
        
        db.session.commit()
        return matches

    @staticmethod
    def _generate_pairings(team_ids):
        """Generate all unique pairings for round-robin"""
        pairings = []
        n = len(team_ids)
        
        for i in range(n):
            for j in range(i + 1, n):
                pairings.append((team_ids[i], team_ids[j]))
        
        return pairings

    @staticmethod
    def _determine_knockout_rounds(num_teams):
        """Determine knockout round names based on number of teams"""
        rounds = []
        
        # Find the power of 2 that's >= num_teams
        power_of_2 = 1
        while power_of_2 < num_teams:
            power_of_2 *= 2
        
        # If not a power of 2, we need preliminary rounds to get to power of 2
        if power_of_2 > num_teams:
            # Add preliminary rounds
            if num_teams > 128:
                rounds.append("Qualifying Round 1")
                rounds.append("Qualifying Round 2")
            elif num_teams > 64:
                rounds.append("Preliminary Round")
            elif num_teams > 32:
                rounds.append("Round of 64")
            elif num_teams > 16:
                rounds.append("Round of 32")
        
        # Now add the standard tournament rounds from power_of_2 down to 2
        current_round = power_of_2
        while current_round >= 2:
            if current_round == 256:
                rounds.append("Round of 256")
            elif current_round == 128:
                rounds.append("Round of 128")
            elif current_round == 64:
                rounds.append("Round of 64")
            elif current_round == 32:
                rounds.append("Round of 32")
            elif current_round == 16:
                rounds.append("Round of 16")
            elif current_round == 8:
                rounds.append("Quarter-Finals")
            elif current_round == 4:
                rounds.append("Semi-Finals")
            elif current_round == 2:
                rounds.append("Final")
            
            current_round //= 2
        
        return rounds

    @staticmethod
    def reschedule_matches(competition_id, start_date, days_between_matches=7):
        """Reschedule all unplayed matches in a competition"""
        matches = Match.query.filter_by(competition_id=competition_id).filter(
            Match.status != 'completed'
        ).order_by(Match.match_date).all()
        
        match_date = start_date
        
        for match in matches:
            match.match_date = match_date
            match_date += timedelta(days=days_between_matches)
        
        db.session.commit()
        return matches

    @staticmethod
    def generate_knockout_from_teams(competition_id, team_ids, start_date=None, days_between_rounds=14):
        """Generate knockout bracket from a list of qualified team_ids"""
        competition = Competition.query.get(competition_id)
        if not competition:
            raise ValueError(f"Competition {competition_id} not found")
        
        if len(team_ids) < 2:
            raise ValueError("Need at least 2 teams for knockout")
        
        if start_date is None:
            start_date = datetime.utcnow()
        
        # Sort teams by seeded position or name for seeding
        comp_teams = CompetitionTeam.query.filter(
            CompetitionTeam.competition_id == competition_id,
            CompetitionTeam.team_id.in_(team_ids)
        ).all()
        
        # Sort by seeded_position, then by team name
        comp_teams.sort(key=lambda ct: (ct.seeded_position or 999, ct.team.name if ct.team else ''))
        sorted_team_ids = [ct.team_id for ct in comp_teams]
        
        # Determine bracket structure
        num_teams = len(sorted_team_ids)
        rounds = SchedulingService._determine_knockout_rounds(num_teams)
        
        matches = []
        match_date = start_date
        
        # Assign teams to bracket positions
        bracket_positions = SchedulingService._assign_bracket_positions(sorted_team_ids)
        
        round_order = 1
        
        for round_name in rounds:
            # Create the knockout round
            ko_round = KnockoutRound(
                competition_id=competition_id,
                round_name=round_name,
                round_order=round_order,
                matches_per_pairing=competition.legs,
                status='pending'
            )
            db.session.add(ko_round)
            db.session.flush()
            
            # Get teams for this round
            round_teams = bracket_positions.get(round_name, [])
            
            # Pair teams
            round_matches = []
            for i in range(0, len(round_teams) - 1, 2):
                home_id = round_teams[i]
                away_id = round_teams[i+1]
                match = Match(
                    home_team_id=home_id,
                    away_team_id=away_id,
                    competition_id=competition_id,
                    knockout_round_id=ko_round.id,
                    match_date=match_date,
                    status=MatchStatus.scheduled,
                    country='Kenya'
                )
                db.session.add(match)
                matches.append(match)
                round_matches.append(match)
                match_date += timedelta(days=days_between_rounds)
            
            # For next round, winners will be assigned later
            # For now, prepare positions for next round
            if round_matches:
                next_round_name = rounds[rounds.index(round_name) + 1] if rounds.index(round_name) + 1 < len(rounds) else None
                if next_round_name:
                    # Placeholder for winners
                    bracket_positions[next_round_name] = [None] * (len(round_matches) // 2 * 2)
            
            round_order += 1
        
        db.session.commit()
        return matches

    @staticmethod
    def _assign_bracket_positions(team_ids):
        """Assign teams to bracket positions for UEFA-style seeding"""
        positions = {}
        num_teams = len(team_ids)
        
        # Determine the starting round based on number of teams
        if num_teams == 16:
            # Round of 16: seed 1 vs 16, 2 vs 15, etc.
            round_teams = []
            for i in range(8):
                round_teams.extend([team_ids[i], team_ids[15-i]])
            positions['Round of 16'] = round_teams
        elif num_teams == 8:
            # Quarter-Finals
            round_teams = []
            for i in range(4):
                round_teams.extend([team_ids[i], team_ids[7-i]])
            positions['Quarter-Finals'] = round_teams
        elif num_teams == 4:
            # Semi-Finals
            positions['Semi-Finals'] = [team_ids[0], team_ids[3], team_ids[1], team_ids[2]]
        elif num_teams == 2:
            # Final
            positions['Final'] = team_ids
        else:
            # For other numbers, pair sequentially
            positions['First Round'] = team_ids
        
        return positions

    @staticmethod
    def generate_next_knockout_round(competition_id, current_round_order):
        """
        Auto-generate the next knockout round based on winners of current round.
        This is called after all matches in a round are completed.
        """
        competition = Competition.query.get(competition_id)
        if not competition:
            raise ValueError(f"Competition {competition_id} not found")
        
        # Get current round
        current_round = KnockoutRound.query.filter_by(
            competition_id=competition_id,
            round_order=current_round_order
        ).first()
        
        if not current_round:
            raise ValueError(f"Round {current_round_order} not found")
        
        # Check if all matches in current round are completed
        incomplete_matches = Match.query.filter_by(
            knockout_round_id=current_round.id
        ).filter(Match.status != MatchStatus.finished).count()
        
        if incomplete_matches > 0:
            raise ValueError("Cannot generate next round - all matches in current round must be completed")
        
        # Get all matches and determine winners
        matches = Match.query.filter_by(knockout_round_id=current_round.id).all()
        winners = []
        
        for match in matches:
            if match.home_score > match.away_score:
                winners.append(match.home_team_id)
            elif match.away_score > match.home_score:
                winners.append(match.away_team_id)
            else:
                # Handle draws - could use extra time, penalties, etc.
                # For now, use home team as winner (admin can override)
                winners.append(match.home_team_id)
        
        # If only one winner, tournament is complete
        if len(winners) <= 1:
            return None
        
        # Create next round
        next_round_order = current_round_order + 1
        
        # Determine next round name
        if len(winners) == 2:
            next_round_name = "Final"
        elif len(winners) == 4:
            next_round_name = "Semi-Finals"
        elif len(winners) == 8:
            next_round_name = "Quarter-Finals"
        else:
            next_round_name = f"Round of {len(winners)}"
        
        next_round = KnockoutRound(
            competition_id=competition_id,
            round_name=next_round_name,
            round_order=next_round_order,
            matches_per_pairing=competition.legs,
            status='pending'
        )
        db.session.add(next_round)
        db.session.flush()
        
        # Generate matches for next round
        matches_list = []
        match_date = datetime.utcnow() + timedelta(days=14)  # Default 2 weeks after current round
        
        for i in range(0, len(winners) - 1, 2):
            match = Match(
                home_team_id=winners[i],
                away_team_id=winners[i+1],
                competition_id=competition_id,
                knockout_round_id=next_round.id,
                match_date=match_date,
                status=MatchStatus.scheduled,
                country='Kenya'
            )
            db.session.add(match)
            matches_list.append(match)
            match_date += timedelta(days=7)
        
        db.session.commit()
        return matches_list

    @staticmethod
    def get_knockout_bracket(competition_id):
        """
        Get the complete knockout bracket structure with all rounds and matches.
        Used for visualization.
        """
        competition = Competition.query.get(competition_id)
        if not competition:
            raise ValueError(f"Competition {competition_id} not found")
        
        # Get all knockout rounds
        rounds = KnockoutRound.query.filter_by(competition_id=competition_id).order_by(
            KnockoutRound.round_order
        ).all()
        
        if not rounds:
            return {}
        
        bracket = {
            'competition_id': str(competition_id),
            'competition_name': competition.name,
            'rounds': []
        }
        
        for round_obj in rounds:
            matches = Match.query.filter_by(knockout_round_id=round_obj.id).order_by(
                Match.match_date
            ).all()
            
            round_data = {
                'round_id': str(round_obj.id),
                'round_order': round_obj.round_order,
                'round_name': round_obj.round_name,
                'status': round_obj.status,
                'matches': []
            }
            
            for match in matches:
                from app.models.team import Team
                home_team = Team.query.get(match.home_team_id)
                away_team = Team.query.get(match.away_team_id)
                
                match_data = {
                    'match_id': str(match.id),
                    'home_team_id': str(match.home_team_id),
                    'home_team_name': home_team.name if home_team else 'TBD',
                    'away_team_id': str(match.away_team_id),
                    'away_team_name': away_team.name if away_team else 'TBD',
                    'home_score': match.home_score,
                    'away_score': match.away_score,
                    'status': match.status.value if match.status else 'scheduled',
                    'match_date': match.match_date.isoformat() if match.match_date else None,
                    'winner_id': str(match.home_team_id) if match.home_score and match.away_score and match.home_score > match.away_score 
                                  else (str(match.away_team_id) if match.away_score and match.home_score and match.away_score > match.home_score else None)
                }
                round_data['matches'].append(match_data)
            
            bracket['rounds'].append(round_data)
        
        return bracket
