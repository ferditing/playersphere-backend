import uuid
from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID

class TournamentMatch(db.Model):
    __tablename__ = "tournament_matches"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tournament_id = db.Column(UUID(as_uuid=True), db.ForeignKey("tournaments.id"))
    match_id = db.Column(UUID(as_uuid=True), db.ForeignKey("matches.id"))

    round = db.Column(db.Text)
    is_group_stage = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())