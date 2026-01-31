import uuid
from app.extensions.db import db
from app.models.match import Match
from app.models.enums import MatchStatus
from app.services.standings_service import StandingsService

class KnockoutService:
    """
    Handles qualification and knockout match generation.
    """

    @staticmethod
    def qualify_teams(tournament_id, slots):
        """
        Selects top N teams from standings.
        """
        standings = StandingsService.compute_standings(tournament_id)
        return standings[:slots]

    @staticmethod
    def generate_bracket(tournament_id, qualified_teams, match_date, venue=None):
        """
        Creates knockout fixtures (1st vs last, etc.)
        """
        matches = []
        total = len(qualified_teams)

        for i in range(total // 2):
            home = qualified_teams[i]["team_id"]
            away = qualified_teams[total - 1 - i]["team_id"]

            match = Match(
                id=uuid.uuid4(),
                home_team_id=home,
                away_team_id=away,
                match_date=match_date,
                venue=venue,
                competition=str(tournament_id),
                status=MatchStatus.scheduled
            )
            db.session.add(match)
            matches.append(match)

        db.session.commit()
        return [m.to_dict() for m in matches]

    @staticmethod
    def resolve_match(match):
        """
        Determines winner after match ends.
        """
        if match.home_score > match.away_score:
            return match.home_team_id
        elif match.away_score > match.home_score:
            return match.away_team_id
        else:
            raise ValueError("Draws not allowed in knockouts")
