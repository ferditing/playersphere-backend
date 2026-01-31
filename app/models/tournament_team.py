import uuid
from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID


class TournamentTeam(db.Model):
    __tablename__ = "tournament_teams"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tournament_id = db.Column(UUID(as_uuid=True), db.ForeignKey("tournaments.id"))
    team_id = db.Column(UUID(as_uuid=True), db.ForeignKey("teams.id"))

    matches_played = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)

    goals_for = db.Column(db.Integer, default=0)
    goals_against = db.Column(db.Integer, default=0)
    goal_difference = db.Column(db.Integer, default=0)

    points = db.Column(db.Integer, default=0)

    fair_play_points = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    # Relationships
    team = db.relationship('Team', foreign_keys=[team_id], backref='tournament_entries')

    def to_dict(self):
        return {
            'id': str(self.id),
            'tournament_id': str(self.tournament_id) if self.tournament_id else None,
            'team_id': str(self.team_id) if self.team_id else None,
            'team': self.team.to_dict() if self.team else None,
            'matches_played': self.matches_played,
            'wins': self.wins,
            'draws': self.draws,
            'losses': self.losses,
            'goals_for': self.goals_for,
            'goals_against': self.goals_against,
            'goal_difference': self.goal_difference,
            'points': self.points,
            'fair_play_points': self.fair_play_points,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }