import uuid
from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime


class CompetitionGroup(db.Model):
    """Groups for group-based competitions (group_knockout format)"""
    __tablename__ = 'competition_groups'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_id = db.Column(UUID(as_uuid=True), db.ForeignKey('competitions.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # e.g., "Group A", "Group B"
    
    # Ordering
    group_order = db.Column(db.Integer, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    competition_teams = db.relationship('CompetitionTeam', backref='group', lazy=True)
    
    __table_args__ = (
        db.UniqueConstraint('competition_id', 'name', name='uq_competition_group_name'),
    )

    def to_dict(self):
        return {
            'id': str(self.id),
            'competition_id': str(self.competition_id),
            'name': self.name,
            'group_order': self.group_order,
            'team_count': len(self.competition_teams),
        }

    def __repr__(self):
        return f'<CompetitionGroup {self.name}>'
