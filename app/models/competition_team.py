import uuid
from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime


class CompetitionTeam(db.Model):
    """Teams participating in a competition"""
    __tablename__ = 'competition_teams'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_id = db.Column(UUID(as_uuid=True), db.ForeignKey('competitions.id'), nullable=False)
    team_id = db.Column(UUID(as_uuid=True), db.ForeignKey('teams.id'), nullable=False)
    
    # Track how team qualified
    manually_added = db.Column(db.Boolean, default=False)
    
    # Seeding position (for knockout or group assignment)
    seeded_position = db.Column(db.Integer, nullable=True)
    
    # Group assignment (for group-based competitions)
    group_id = db.Column(UUID(as_uuid=True), db.ForeignKey('competition_groups.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    team = db.relationship('Team', backref='competition_teams', lazy=True)
    
    __table_args__ = (
        db.UniqueConstraint('competition_id', 'team_id', name='uq_competition_team'),
    )

    def to_dict(self):
        return {
            'id': str(self.id),
            'competition_id': str(self.competition_id),
            'team_id': str(self.team_id),
            'team_name': self.team.name if self.team else None,
            'manually_added': self.manually_added,
            'seeded_position': self.seeded_position,
            'group_id': str(self.group_id) if self.group_id else None,
        }

    def __repr__(self):
        return f'<CompetitionTeam {self.team.name if self.team else "N/A"}>'
