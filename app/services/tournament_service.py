import uuid
from app.extensions.db import db
from app.models.tournament import Tournament
from app.models.tournament_team import TournamentTeam
import datetime


class TournamentService:

    @staticmethod
    def create_tournament(data, coach_id):
        # Map incoming payload fields to the Tournament model columns.
        # Avoid passing unexpected kwargs like `format` or `tie_breaker`.
        def _parse_date(s):
            try:
                return datetime.date.fromisoformat(s)
            except Exception:
                return None

        tournament = Tournament(
            id=uuid.uuid4(),
            name=data.get("name"),
            description=data.get("description"),
            tournament_type=(data.get("type") or data.get("tournament_type") or data.get("format") or "league"),
            slots=(data.get("number_of_teams") or data.get("slots") or 3),
            created_by=coach_id,
            start_date=_parse_date(data.get("start_date")) if data.get("start_date") else None,
            end_date=_parse_date(data.get("end_date")) if data.get("end_date") else None,
        )
        db.session.add(tournament)
        db.session.commit()
        return tournament

    @staticmethod
    def add_team(tournament_id, team_id):
        entry = TournamentTeam(
            id=uuid.uuid4(),
            tournament_id=tournament_id,
            team_id=team_id
        )
        db.session.add(entry)
        db.session.commit()
        return entry

    @staticmethod
    def list_teams(tournament_id):
        teams = TournamentTeam.query.filter_by(
            tournament_id=tournament_id
        ).all()

        return [t.to_dict() for t in teams]
