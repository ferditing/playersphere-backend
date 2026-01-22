import uuid
from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID

class TeamStats(db.Model):
    __tablename__ = "team_stats"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = db.Column(UUID(as_uuid=True), db.ForeignKey("teams.id"), nullable=False)

    season = db.Column(db.Text, default="2024")
    matches_played = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    goals_for = db.Column(db.Integer, default=0)
    goals_against = db.Column(db.Integer, default=0)
    clean_sheets = db.Column(db.Integer, default=0)

    updated_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': str(self.id),
            'team_id': str(self.team_id),
            'season': self.season,
            'matches_played': self.matches_played,
            'wins': self.wins,
            'draws': self.draws,
            'losses': self.losses,
            'goals_for': self.goals_for,
            'goals_against': self.goals_against,
            'clean_sheets': self.clean_sheets,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
