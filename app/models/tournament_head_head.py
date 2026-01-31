import uuid
from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID

class TournamentHeadToHead(db.Model):
    __tablename__ = "tournament_head_to_head"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tournament_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("tournaments.id", ondelete="CASCADE"),
        nullable=False
    )

    team_a_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False
    )

    team_b_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False
    )

    points_a = db.Column(db.Integer, default=0)
    points_b = db.Column(db.Integer, default=0)

    goal_diff_a = db.Column(db.Integer, default=0)
    goal_diff_b = db.Column(db.Integer, default=0)

    __table_args__ = (
        db.UniqueConstraint(
            "tournament_id", "team_a_id", "team_b_id",
            name="unique_h2h_pair"
        ),
    )
