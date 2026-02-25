import uuid
from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID


class Region(db.Model):
    __tablename__ = 'regions'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    country_id = db.Column(UUID(as_uuid=True), db.ForeignKey('countries.id'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    code = db.Column(db.String(20), nullable=True)  # e.g., 'KE_CENT' for Central Kenya
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Relationships
    counties = db.relationship('County', backref='region', lazy=True, cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('country_id', 'name', name='uq_region_country_name'),
    )

    def to_dict(self):
        return {
            'id': str(self.id),
            'country_id': str(self.country_id),
            'name': self.name,
            'code': self.code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Region {self.name}>'
