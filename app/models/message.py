import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.extensions.db import db

class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    sender_id = db.Column(UUID(as_uuid=True), db.ForeignKey("coaches.id"), nullable=False)
    recipient_id = db.Column(UUID(as_uuid=True), db.ForeignKey("coaches.id"), nullable=False)

    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': str(self.id),
            'sender_id': str(self.sender_id),
            'recipient_id': str(self.recipient_id),
            'content': self.content,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
