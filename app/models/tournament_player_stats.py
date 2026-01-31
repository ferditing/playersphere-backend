import uuid
from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID

class TournamentPlayerStats(db.Model):
    __tablename__ = "tournament_player_stats"

    id = db.Column(UUID(as_uuid=True), primary_key = True, default=uuid.uuid4)
    
    tournament_id = db.Column(UUID(as_uuid=True), db.ForeignKey("tournamnets.id"))
    player_id = db.Column(UUID(as_uuid=True), db.ForeignKey("players.id"))
    team_id = db.Column(UUID(as_uuid=True), db.ForeignKey("teams.id"))

    matches_played = db.Column(db.Integer, Default=0)
    minutes_played = db.Column(db.Integer, Default=0)

    goals = db.Column(db.Integer, Default=0)
    assists = db.Column(db.Integer, Default=0)

    yellow_cards = db.Column(db.Integer, Default=0)
    red_cards = db.Column(db.Integer, Default=0)