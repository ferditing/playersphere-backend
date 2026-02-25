import uuid
from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime


class CompetitionAdvancementRule(db.Model):
    """Rules for advancing teams from one competition to the next"""
    __tablename__ = 'competition_advancement_rules'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_competition_id = db.Column(UUID(as_uuid=True), db.ForeignKey('competitions.id'), nullable=False)
    to_competition_id = db.Column(UUID(as_uuid=True), db.ForeignKey('competitions.id'), nullable=True)
    
    # Rule type
    rule_type = db.Column(db.String(50), nullable=False)
    # 'top_positions' - advance top N by standings
    # 'group_winners' - advance group winners from group_knockout
    # 'knockout_winner' - only knockout winner advances
    # 'manual_only' - no auto-advancement, only manual
    
    # Positions to advance (for 'top_positions')
    advancement_positions = db.Column(db.Integer, nullable=True)  # e.g., top 4 advance
    
    # Auto-apply flag
    auto_apply = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('from_competition_id', 'rule_type', name='uq_advancement_rule_per_competition'),
    )

    def to_dict(self):
        return {
            'id': str(self.id),
            'from_competition_id': str(self.from_competition_id),
            'to_competition_id': str(self.to_competition_id) if self.to_competition_id else None,
            'rule_type': self.rule_type,
            'advancement_positions': self.advancement_positions,
            'auto_apply': self.auto_apply,
        }

    def __repr__(self):
        return f'<CompetitionAdvancementRule {self.rule_type}>'
