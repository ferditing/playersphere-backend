import uuid
from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID


class Country(db.Model):
    __tablename__ = 'countries'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.Text, unique=True, nullable=False)
    code = db.Column(db.String(2), unique=True, nullable=False)  # ISO 3166-1 alpha-2 (e.g., 'KE', 'UG')
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Relationships
    regions = db.relationship('Region', backref='country', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'code': self.code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Country {self.name} ({self.code})>'
