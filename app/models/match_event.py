import uuid
from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID
from app.models.enums import EventType

class MatchEvent(db.Model):
    __tablename__ = "match_events"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    match_id = db.Column(UUID(as_uuid=True), db.ForeignKey("matches.id"), nullable=False)
    team_id = db.Column(UUID(as_uuid=True), db.ForeignKey("teams.id"), nullable=False)
    player_id = db.Column(UUID(as_uuid=True), db.ForeignKey("players.id"))

    event_type = db.Column(db.Enum(EventType), nullable=False)
    minute = db.Column(db.Integer, nullable=False)
    additional_info = db.Column(db.JSON, default=dict)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    team = db.relationship('Team', foreign_keys=[team_id], backref='events')
    player = db.relationship('Player', foreign_keys=[player_id], backref='events')

    def to_dict(self):
        return {
            'id': str(self.id),
            'match_id': str(self.match_id),
            'team_id': str(self.team_id),
            'player_id': str(self.player_id) if self.player_id else None,
            'event_type': self.event_type.value if self.event_type else None,
            'minute': self.minute,
            'additional_info': self.additional_info,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
