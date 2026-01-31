import uuid
from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID
from app.models.tournament import Tournament

class TournamentInvite(db.Model):
    __tablename__ = "tournament_invites"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tournament_id = db.Column(UUID(as_uuid=True), db.ForeignKey("tournaments.id"), nullable=False)
    from_coach_id = db.Column(UUID(as_uuid=True), db.ForeignKey("coaches.id"))
    to_coach_id = db.Column(UUID(as_uuid=True), db.ForeignKey("coaches.id"))
    team_id = db.Column(UUID(as_uuid=True), db.ForeignKey("teams.id"))


    status = db.Column(
        db.Enum("pending", "accepted", "rejected", name="invite_status"),
        default="pending"
    )

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': str(self.id),
            'tournament_id': str(self.tournament_id) if self.tournament_id else None,
            'from_coach_id': str(self.from_coach_id) if self.from_coach_id else None,
            'to_coach_id': str(self.to_coach_id) if self.to_coach_id else None,
            'team_id': str(self.team_id) if self.team_id else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }