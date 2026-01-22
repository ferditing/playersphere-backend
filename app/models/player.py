import uuid
from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID

class Player(db.Model):
    __tablename__ = "players"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = db.Column(UUID(as_uuid=True), db.ForeignKey("teams.id"))

    full_name = db.Column(db.Text, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    position = db.Column(db.Text, nullable=False)

    jersey_number = db.Column(db.Integer)
    height_cm = db.Column(db.Integer)
    weight_kg = db.Column(db.Integer)
    preferred_foot = db.Column(db.Text)
    photo_url = db.Column(db.Text)

    country = db.Column(db.Text, default="Kenya")
    region = db.Column(db.Text)
    city = db.Column(db.Text)

    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Relationships
    team = db.relationship('Team', back_populates='players', lazy=True)

    def to_dict(self):
        return {
            'id': str(self.id),
            'team_id': str(self.team_id) if self.team_id else None,
            'team': self.team.to_dict() if self.team else None,
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'position': self.position,
            'jersey_number': self.jersey_number,
            'height_cm': self.height_cm,
            'weight_kg': self.weight_kg,
            'preferred_foot': self.preferred_foot,
            'photo_url': self.photo_url,
            'country': self.country,
            'region': self.region,
            'city': self.city,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
