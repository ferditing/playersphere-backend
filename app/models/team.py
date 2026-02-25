import uuid
from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID

class Team(db.Model):
    __tablename__ = "teams"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coach_id = db.Column(UUID(as_uuid=True), db.ForeignKey("coaches.id"), nullable=False)

    name = db.Column(db.Text, nullable=False)
    logo_url = db.Column(db.Text)
    founded_year = db.Column(db.Integer)

    country = db.Column(db.Text, default="Kenya")
    region = db.Column(db.Text)
    city = db.Column(db.Text)
    area = db.Column(db.Text)

    team_type = db.Column(db.Text)
    backup_email_1 = db.Column(db.Text)
    backup_email_2 = db.Column(db.Text)
    county_id = db.Column(UUID(as_uuid=True), db.ForeignKey('counties.id'), nullable=True)
    created_by_admin_id = db.Column(UUID(as_uuid=True), nullable=True)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Relationships
    players = db.relationship('Player', back_populates='team', lazy=True)

    def to_dict(self):
        return {
            'id': str(self.id),
            'coach_id': str(self.coach_id),
            'name': self.name,
            'logo_url': self.logo_url,
            'founded_year': self.founded_year,
            'country': self.country,
            'region': self.region,
            'city': self.city,
            'area': self.area,
            'team_type': self.team_type,
            'backup_email_1': self.backup_email_1,
            'backup_email_2': self.backup_email_2,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
