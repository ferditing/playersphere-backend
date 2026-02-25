import uuid
from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime


class KnockoutRound(db.Model):
    """Knockout rounds for knockout/group_knockout competitions"""
    __tablename__ = 'knockout_rounds'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_id = db.Column(UUID(as_uuid=True), db.ForeignKey('competitions.id'), nullable=False)
    
    # Round information
    round_name = db.Column(db.String(100), nullable=False)  # e.g., "Round of 16", "Semi-Final", "Final"
    round_order = db.Column(db.Integer, nullable=False)  # 1 = first round (qualifying), increasing order
    
    # Structure
    matches_per_pairing = db.Column(db.Integer, default=1)  # 1 or 2 (legs)
    
    # Status
    status = db.Column(db.String(50), default='pending')  # 'pending', 'ongoing', 'completed'
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    matches = db.relationship('Match', backref='knockout_round', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('competition_id', 'round_order', name='uq_competition_round_order'),
    )

    def to_dict(self):
        return {
            'id': str(self.id),
            'competition_id': str(self.competition_id),
            'round_name': self.round_name,
            'round_order': self.round_order,
            'matches_per_pairing': self.matches_per_pairing,
            'status': self.status,
            'match_count': len(self.matches),
        }

    def __repr__(self):
        return f'<KnockoutRound {self.round_name}>'
