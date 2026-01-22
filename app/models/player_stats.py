import uuid
from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID

from app.extensions.db import db


class PlayerStats(db.Model):
    __tablename__ = "player_stats"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = db.Column(UUID(as_uuid=True), db.ForeignKey("players.id"), nullable=False)

    season = db.Column(db.Text, default="2024")
    matches_played = db.Column(db.Integer, default=0)
    minutes_played = db.Column(db.Integer, default=0)
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    yellow_cards = db.Column(db.Integer, default=0)
    red_cards = db.Column(db.Integer, default=0)
    shots_on_target = db.Column(db.Integer, default=0)
    shots_off_target = db.Column(db.Integer, default=0)

    updated_at = db.Column(db.DateTime, server_default=db.func.now())
