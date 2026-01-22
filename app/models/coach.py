import uuid
from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import generate_password_hash, check_password_hash

class Coach(db.Model):
    __tablename__ = 'coaches'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), unique=True, nullable=True)  # Made nullable for JWT auth
    full_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    phone = db.Column(db.Text, nullable=False, unique=True)
    whatsapp_number = db.Column(db.Text)
    password_hash = db.Column(db.Text, nullable=False)  # Added for JWT auth
    country = db.Column(db.Text, default="Kenya")
    region = db.Column(db.Text)
    city = db.Column(db.Text)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Relationships
    teams = db.relationship('Team', backref='coach', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id) if self.user_id else None,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'whatsapp_number': self.whatsapp_number,
            'country': self.country,
            'region': self.region,
            'city': self.city,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }