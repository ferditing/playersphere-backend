import uuid
from datetime import datetime, timedelta

from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import CheckConstraint
from werkzeug.security import check_password_hash, generate_password_hash


class Admin(db.Model):
    __tablename__ = "admins"

    id =  db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    password_hash = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    role = db.Column(db.Text, nullable=False)
    county_id = db.Column(UUID(as_uuid=True), db.ForeignKey('counties.id'), nullable=True)

    __table_args__ = (
        CheckConstraint("role IN ('super_admin', 'county_admin', 'national_admin')"),
    )

    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)

    def set_password(self, password):
        """Generate password hash"""
        self.password_hash = generate_password_hash(password)

    def to_dict(self):
        """Convert admin to dictionary"""
        return {
            'id': str(self.id),
            'full_name': self.full_name,
            'email': self.email,
            'role': self.role,
            'county_id': str(self.county_id) if self.county_id else None,
            'county_name': self.county.name if self.county else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

