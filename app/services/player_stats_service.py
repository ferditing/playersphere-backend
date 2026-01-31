from sqlalchemy import func
from sqlalchemy import case
from app.extensions.db import db
from app.models.player import Player
from app.models.match_event import MatchEvent
from app.models.match import Match
from app.models.enums import EventType

class PlayerStatsService:

    @staticmethod
    def top_scorers(tournament_id, limit=10):
        """
        Returns top scorers in a tournament.
        """
        results = (
            db.session.query(
                Player.id,
                Player.full_name,
                func.count(MatchEvent.id).label("goals")
            )
            .join(MatchEvent, MatchEvent.player_id == Player.id)
            .join(Match, Match.id == MatchEvent.match_id)
            .filter(
                Match.competition == str(tournament_id),
                MatchEvent.event_type.in_([EventType.goal, EventType.penalty_goal])
            )
            .group_by(Player.id)
            .order_by(func.count(MatchEvent.id).desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "player_id": str(r.id),
                "player_name": r.full_name,
                "goals": r.goals
            }
            for r in results
        ]

    @staticmethod
    def disciplinary(tournament_id):
        """
        Yellow & red cards per player.
        """
        results = (
            db.session.query(
                Player.id,
                Player.full_name,
                func.sum(
                    case([(MatchEvent.event_type == EventType.yellow_card, 1)], else_=0)
                ).label("yellow_cards"),
                func.sum(
                    case([(MatchEvent.event_type == EventType.red_card, 1)], else_=0)
                ).label("red_cards"),
            )
            .join(MatchEvent, MatchEvent.player_id == Player.id)
            .join(Match, Match.id == MatchEvent.match_id)
            .filter(Match.competition == str(tournament_id))
            .group_by(Player.id)
            .all()
        )

        return [
            {
                "player_id": str(r.id),
                "player_name": r.full_name,
                "yellow_cards": r.yellow_cards,
                "red_cards": r.red_cards
            }
            for r in results
        ]
