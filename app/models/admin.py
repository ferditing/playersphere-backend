import uuid
from datetime import datetime, timedelta

from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import CheckConstraint


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
