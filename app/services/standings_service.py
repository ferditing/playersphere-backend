from collections import defaultdict
from sqlalchemy import and_

from app.extensions.db import db
from app.models.match import Match
from app.models.enums import MatchStatus
from app.models.team import Team
from app.models.tournament_team import TournamentTeam


class StandingsService:
    """
    League Table / Tournament Standings Engine

    This service is stateless.
    You can rebuild standings anytime from match data.
    """

    POINTS_WIN = 3
    POINTS_DRAW = 1
    POINTS_LOSS = 0

    @staticmethod
    def get_standings(tournament_id):
        """
        Public entry point.
        Returns sorted league table for a tournament.
        """

        teams = StandingsService._get_tournament_teams(tournament_id)
        matches = StandingsService._get_finished_matches(tournament_id)

        table = StandingsService._initialize_table(teams)
        StandingsService._apply_matches(table, matches)
        StandingsService._sort_table(table)

        return list(table.values())

    # ---------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------

    @staticmethod
    def _get_tournament_teams(tournament_id):
        """
        Fetch all teams registered in a tournament
        """
        return (
            db.session.query(Team)
            .join(TournamentTeam, TournamentTeam.team_id == Team.id)
            .filter(TournamentTeam.tournament_id == tournament_id)
            .all()
        )

    @staticmethod
    def _get_finished_matches(tournament_id):
        """
        Fetch all completed matches for tournament
        """
        return (
            Match.query
            .filter(
                and_(
                    Match.competition == str(tournament_id),
                    Match.status == MatchStatus.finished
                )
            )
            .all()
        )

    @staticmethod
    def _initialize_table(teams):
        """
        Create empty table rows for each team
        """
        table = {}

        for team in teams:
            table[team.id] = {
                "team_id": team.id,
                "team_name": team.name,

                "played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,

                "goals_for": 0,
                "goals_against": 0,
                "goal_difference": 0,

                "points": 0,
            }

        return table

    @staticmethod
    def _apply_matches(table, matches):
        """
        Update standings based on match results
        """

        for match in matches:
            home = table.get(match.home_team_id)
            away = table.get(match.away_team_id)

            # Safety check (in case of orphaned data)
            if not home or not away:
                continue

            home_score = match.home_score
            away_score = match.away_score

            # Played
            home["played"] += 1
            away["played"] += 1

            # Goals
            home["goals_for"] += home_score
            home["goals_against"] += away_score

            away["goals_for"] += away_score
            away["goals_against"] += home_score

            # Goal difference
            home["goal_difference"] = (
                home["goals_for"] - home["goals_against"]
            )
            away["goal_difference"] = (
                away["goals_for"] - away["goals_against"]
            )

            # Points logic
            if home_score > away_score:
                home["wins"] += 1
                away["losses"] += 1

                home["points"] += StandingsService.POINTS_WIN
                away["points"] += StandingsService.POINTS_LOSS

            elif home_score < away_score:
                away["wins"] += 1
                home["losses"] += 1

                away["points"] += StandingsService.POINTS_WIN
                home["points"] += StandingsService.POINTS_LOSS

            else:
                home["draws"] += 1
                away["draws"] += 1

                home["points"] += StandingsService.POINTS_DRAW
                away["points"] += StandingsService.POINTS_DRAW

    @staticmethod
    def _sort_table(table):
        """
        Sort standings using official competition rules
        """

        sorted_rows = sorted(
            table.values(),
            key=lambda x: (
                x["points"],
                x["goal_difference"],
                x["goals_for"],
                x["team_name"].lower(),  # deterministic fallback
            ),
            reverse=True
        )

        # Reassign rank positions
        for position, row in enumerate(sorted_rows, start=1):
            row["position"] = position

        # Re-map table
        table.clear()
        for row in sorted_rows:
            table[row["team_id"]] = row
