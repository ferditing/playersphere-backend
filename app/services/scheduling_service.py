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
        
        # Generate preliminary rounds if needed (for large numbers of teams)
        remaining_teams = team_ids
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
            db.session.flush()  # Get the ID
            
            # Pair teams in this round
            pairings = [(remaining_teams[i], remaining_teams[i+1]) 
                       for i in range(0, len(remaining_teams), 2)]
            
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
            
            # For next round, we'd have half the teams (winners only)
            # This is a template - actual advancement happens after matches
            remaining_teams = [remaining_teams[i] for i in range(0, len(remaining_teams), 2)]
            match_date += timedelta(days=days_between_rounds)
            round_order += 1
        
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
        
        # After group stage, create knockout round structure (but don't pair yet)
        ko_round = KnockoutRound(
            competition_id=competition_id,
            round_name="Knockout",
            round_order=num_groups + 1,
            matches_per_pairing=competition.legs,
            status='pending'
        )
        db.session.add(ko_round)
        
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
        
        # Check if we need preliminary rounds
        power_of_2 = 1
        while power_of_2 < num_teams:
            power_of_2 *= 2
        
        # If not a power of 2, we need preliminary rounds
        if power_of_2 > num_teams:
            need_preliminary = power_of_2 // 2
            byes = power_of_2 - num_teams
            
            if num_teams > 128:
                rounds.append("Qualifying Round 1")
                rounds.append("Qualifying Round 2")
            elif num_teams > 64:
                rounds.append("Preliminary Round")
            elif num_teams > 32:
                rounds.append("Round of 64")
            elif num_teams > 16:
                rounds.append("Round of 32")
        
        # Standard knockout rounds (working backwards from power of 2)
        if power_of_2 >= 2:
            rounds.append("Round of 2" if power_of_2 == 2 else f"Round of {power_of_2}")
        
        if power_of_2 >= 4:
            rounds.append("Quarter-Finals")
        
        if power_of_2 >= 8:
            rounds.append("Semi-Finals")
        
        if power_of_2 >= 16:
            rounds.append("Final")
        
        # Reverse to get chronological order
        return list(reversed(rounds))

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
    def get_schedule(competition_id, group_id=None, knockout_round_id=None):
        """Get schedule/fixtures for a competition, optionally filtered by group or round"""
        query = Match.query.filter_by(competition_id=competition_id)
        
        if group_id:
            query = query.filter_by(group_id=group_id)
        
        if knockout_round_id:
            query = query.filter_by(knockout_round_id=knockout_round_id)
        
        matches = query.order_by(Match.match_date).all()
        
        return [match.to_dict() for match in matches]
