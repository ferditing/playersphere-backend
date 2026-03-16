import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.extensions.db import db

class Ticket(db.Model):
    __tablename__ = "tickets"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    from_name = db.Column(db.String(100), nullable=False)
    team_name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    ticket_type = db.Column(db.String(50), nullable=False)  # request, complaint, inquiry, alert
    status = db.Column(db.String(50), nullable=False, default='unread')  # unread, read, resolved

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def to_dict(self):
        return {
            'id': str(self.id),
            'from': self.from_name,
            'team': self.team_name,
            'subject': self.subject,
            'message': self.message,
            'type': self.ticket_type,
            'status': self.status,
            'date': self.created_at.isoformat() if self.created_at else None,
        }