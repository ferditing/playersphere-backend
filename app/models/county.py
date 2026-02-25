import uuid
from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID


class County(db.Model):
    __tablename__ = 'counties'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    region_id = db.Column(UUID(as_uuid=True), db.ForeignKey('regions.id'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    code = db.Column(db.String(20), nullable=True)  # e.g., 'KE_NAIROBI'
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Relationships
    wards = db.relationship('Ward', backref='county', lazy=True, cascade='all, delete-orphan')
    coaches = db.relationship('Coach', backref='county', foreign_keys='Coach.county_id', lazy=True)
    teams = db.relationship('Team', backref='county', foreign_keys='Team.county_id', lazy=True)
    admins = db.relationship('Admin', backref='county', foreign_keys='Admin.county_id', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('region_id', 'name', name='uq_county_region_name'),
    )

    def to_dict(self):
        return {
            'id': str(self.id),
            'region_id': str(self.region_id),
            'name': self.name,
            'code': self.code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<County {self.name}>'
