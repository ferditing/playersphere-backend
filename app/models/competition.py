import uuid
from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime


class Competition(db.Model):
    """Generic competition engine supporting multiple formats and stages"""
    __tablename__ = 'competitions'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    season_id = db.Column(UUID(as_uuid=True), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    
    # Stage level: county, regional, national
    stage_level = db.Column(db.String(50), nullable=False)  
    
    # Location constraints (optional)
    region_id = db.Column(UUID(as_uuid=True), db.ForeignKey('regions.id'), nullable=True)
    county_id = db.Column(UUID(as_uuid=True), db.ForeignKey('counties.id'), nullable=True)
    
    # Format: round_robin, knockout, group_knockout
    format_type = db.Column(db.String(50), nullable=False, default='knockout')
    
    # Legs: 1 or 2 (single or double leg)
    legs = db.Column(db.Integer, default=1, nullable=False)
    
    # Points system
    points_win = db.Column(db.Integer, default=3)
    points_draw = db.Column(db.Integer, default=1)
    points_loss = db.Column(db.Integer, default=0)
    
    # Status
    status = db.Column(db.String(50), default='draft')  # draft, ongoing, completed
    
    # Constraints
    max_teams = db.Column(db.Integer, nullable=True)  # Optional limit
    min_teams = db.Column(db.Integer, default=2)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teams = db.relationship('CompetitionTeam', backref='competition', lazy=True, cascade='all, delete-orphan')
    groups = db.relationship('CompetitionGroup', backref='competition', lazy=True, cascade='all, delete-orphan')
    knockout_rounds = db.relationship('KnockoutRound', backref='competition', lazy=True, cascade='all, delete-orphan')
    matches = db.relationship('Match', backref='competition', lazy=True, foreign_keys='Match.competition_id')
    advancement_rules_from = db.relationship('CompetitionAdvancementRule', foreign_keys='CompetitionAdvancementRule.from_competition_id', backref='source_competition', lazy=True)
    advancement_rules_to = db.relationship('CompetitionAdvancementRule', foreign_keys='CompetitionAdvancementRule.to_competition_id', backref='destination_competition', lazy=True)
    
    __table_args__ = (
        db.UniqueConstraint('season_id', 'name', name='uq_competition_season_name'),
    )

    def to_dict(self):
        return {
            'id': str(self.id),
            'season_id': str(self.season_id),
            'name': self.name,
            'stage_level': self.stage_level,
            'format_type': self.format_type,
            'legs': self.legs,
            'status': self.status,
            'points_win': self.points_win,
            'points_draw': self.points_draw,
            'points_loss': self.points_loss,
            'max_teams': self.max_teams,
            'region_id': str(self.region_id) if self.region_id else None,
            'county_id': str(self.county_id) if self.county_id else None,
        }

    def __repr__(self):
        return f'<Competition {self.name} ({self.format_type})>'
