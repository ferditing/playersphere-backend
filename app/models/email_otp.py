import uuid
from datetime import datetime, timedelta

from app.extensions.db import db
from sqlalchemy.dialects.postgresql import UUID

class EmailOTP(db.Model):
    __tablename__ = "email_otps"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    email = db.Column(db.Text, nullable=False, index=True)
    otp_code = db.Column(db.Text, nullable=False)

    purpose = db.Column(db.Text, nullable=False, default="signup")
    is_used = db.Column(db.Boolean, default=False)

    expires_at = db.Column(db.DateTime, nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    @staticmethod
    def new(email: str, otp_code: str, minutes_valid: int = 10):
        return EmailOTP(
            email=email.lower().strip(),
            otp_code=otp_code,
            expires_at=datetime.utcnow() + timedelta(minutes=minutes_valid),
            is_used=False
        )
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at