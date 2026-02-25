import uuid
from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID
from app.models.enums import MatchStatus

class Match(db.Model):
    __tablename__ = "matches"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    home_team_id = db.Column(UUID(as_uuid=True), db.ForeignKey("teams.id"), nullable=False)
    away_team_id = db.Column(UUID(as_uuid=True), db.ForeignKey("teams.id"), nullable=False)
    
    # Competition structure
    competition_id = db.Column(UUID(as_uuid=True), db.ForeignKey("competitions.id"), nullable=True)
    group_id = db.Column(UUID(as_uuid=True), db.ForeignKey("competition_groups.id"), nullable=True)
    knockout_round_id = db.Column(UUID(as_uuid=True), db.ForeignKey("knockout_rounds.id"), nullable=True)

    match_date = db.Column(db.DateTime, nullable=False)
    venue = db.Column(db.Text)

    country = db.Column(db.Text, default="Kenya")
    region = db.Column(db.Text)
    city = db.Column(db.Text)

    status = db.Column(db.Enum(MatchStatus), default=MatchStatus.scheduled)
    home_score = db.Column(db.Integer, default=0)
    away_score = db.Column(db.Integer, default=0)
    current_minute = db.Column(db.Integer, default=0)
    started_at = db.Column(db.DateTime)
    ended_at = db.Column(db.DateTime)

    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey("coaches.id"))

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Relationships
    events = db.relationship('MatchEvent', backref='match', lazy=True)
    home_team = db.relationship('Team', foreign_keys=[home_team_id], backref='home_matches')
    away_team = db.relationship('Team', foreign_keys=[away_team_id], backref='away_matches')

    def to_dict(self):
        return {
            'id': str(self.id),
            'home_team_id': str(self.home_team_id),
            'away_team_id': str(self.away_team_id),
            'home_team': self.home_team.to_dict() if self.home_team else None,
            'away_team': self.away_team.to_dict() if self.away_team else None,
            'competition_id': str(self.competition_id) if self.competition_id else None,
            'group_id': str(self.group_id) if self.group_id else None,
            'knockout_round_id': str(self.knockout_round_id) if self.knockout_round_id else None,
            'match_date': self.match_date.isoformat() if self.match_date else None,
            'venue': self.venue,
            'country': self.country,
            'region': self.region,
            'city': self.city,
            'status': self.status.value if self.status else None,
            'home_score': self.home_score,
            'away_score': self.away_score,
            'current_minute': self.current_minute,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'created_by': str(self.created_by) if self.created_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
