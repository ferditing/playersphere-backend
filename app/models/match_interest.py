import uuid
from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID
from app.models.enums import MatchInterestStatus

class MatchInterest(db.Model):
    __tablename__ = "match_interests"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    requesting_coach_id = db.Column(UUID(as_uuid=True), db.ForeignKey("coaches.id"), nullable=False)
    requesting_team_id = db.Column(UUID(as_uuid=True), db.ForeignKey("teams.id"), nullable=False)
    target_team_id = db.Column(UUID(as_uuid=True), db.ForeignKey("teams.id"), nullable=False)

    proposed_date = db.Column(db.DateTime, nullable=False)
    proposed_venue = db.Column(db.Text)
    message = db.Column(db.Text)

    status = db.Column(db.Enum(MatchInterestStatus), default=MatchInterestStatus.pending)
    responded_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    requesting_team = db.relationship('Team', foreign_keys=[requesting_team_id], backref='sent_interests')
    target_team = db.relationship('Team', foreign_keys=[target_team_id], backref='received_interests')
    requesting_coach = db.relationship('Coach', foreign_keys=[requesting_coach_id], backref='sent_interests')

    def to_dict(self):
        return {
            'id': str(self.id),
            'requesting_coach_id': str(self.requesting_coach_id),
            'requesting_team_id': str(self.requesting_team_id),
            'target_team_id': str(self.target_team_id),
            'proposed_date': self.proposed_date.isoformat() if self.proposed_date else None,
            'proposed_venue': self.proposed_venue,
            'message': self.message,
            'status': self.status.value if self.status else None,
            'responded_at': self.responded_at.isoformat() if self.responded_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'requesting_team': self.requesting_team.to_dict() if self.requesting_team else None,
            'target_team': self.target_team.to_dict() if self.target_team else None,
            'requesting_coach': self.requesting_coach.to_dict() if self.requesting_coach else None,
        }
