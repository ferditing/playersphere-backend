import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.extensions.db import db

class NotificationLog(db.Model):
    __tablename__ = "notification_logs"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    channel = db.Column(db.String(50))  # whatsapp, email (future)
    recipient = db.Column(db.String(100))
    message = db.Column(db.Text)

    status = db.Column(db.String(50))  # sent, failed
    external_id = db.Column(db.String(100))  # WhatsApp message ID

    created_at = db.Column(db.DateTime, server_default=db.func.now())
