from app.extensions.db import db
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Tournament(db.Model):
    __tablename__ = "tournaments"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)

    tournament_type = db.Column(
        db.Enum("league", "knockout", "group_knockout", name="tournament_type"),
        nullable=False
    )

    points_win = db.Column(db.Integer, default=3)
    points_draw = db.Column(db.Integer, default=1)
    points_loss = db.Column(db.Integer, default=0)

    tiebreaker_order = db.Column(
        db.ARRAY(db.Text),
        default=["points", "goal_difference", "goals_for", "head_to_head", "fair_play"]
    )

    status = db.Column(
        db.Enum("draft", "ongoing", "completed", name="tournament_status"),
        default="draft"
    )
    slots = db.Column(db.Integer, nullable=False)

    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey("coaches.id"), nullable=False)

    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'tournament_type': self.tournament_type,
            'points_win': self.points_win,
            'points_draw': self.points_draw,
            'points_loss': self.points_loss,
            'tiebreaker_order': list(self.tiebreaker_order) if self.tiebreaker_order is not None else None,
            'status': self.status,
            'slots': self.slots,
            'created_by': str(self.created_by) if self.created_by else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
