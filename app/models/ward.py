import uuid
from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID


class Ward(db.Model):
    __tablename__ = 'wards'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    county_id = db.Column(UUID(as_uuid=True), db.ForeignKey('counties.id'), nullable=False)
    constituency_id = db.Column(UUID(as_uuid=True), db.ForeignKey('constituencies.id'), nullable=True)
    name = db.Column(db.Text, nullable=False)
    code = db.Column(db.String(20), nullable=True)
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    __table_args__ = (
        db.UniqueConstraint('constituency_id', 'name', name='uq_ward_constituency_name'),
    )

    def to_dict(self):
        return {
            'id': str(self.id),
            'county_id': str(self.county_id),
            'name': self.name,
            'code': self.code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Ward {self.name}>'
