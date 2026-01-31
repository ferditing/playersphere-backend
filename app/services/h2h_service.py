from collections import defaultdict
from app.extensions.db import db
from app.models.match import Match

class HeadToHeadService:
    """
    Computes head-to-head results for tied teams in a tournament.
    """

    @staticmethod
    def compute(tournament_id, team_ids):
        """
        Returns H2H stats between given teams.
        """
        stats = defaultdict(lambda: {
            "points": 0,
            "goals_for": 0,
            "goals_against": 0,
            "goal_diff": 0
        })

        matches = Match.query.filter(
            Match.competition == str(tournament_id),
            Match.home_team_id.in_(team_ids),
            Match.away_team_id.in_(team_ids),
            Match.status == "finished"
        ).all()

        for match in matches:
            h, a = match.home_team_id, match.away_team_id
            hs, as_ = match.home_score, match.away_score

            stats[h]["goals_for"] += hs
            stats[h]["goals_against"] += as_
            stats[a]["goals_for"] += as_
            stats[a]["goals_against"] += hs

            if hs > as_:
                stats[h]["points"] += 3
            elif hs < as_:
                stats[a]["points"] += 3
            else:
                stats[h]["points"] += 1
                stats[a]["points"] += 1

        for t in stats:
            stats[t]["goal_diff"] = (
                stats[t]["goals_for"] - stats[t]["goals_against"]
            )

        return stats
