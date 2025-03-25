from datetime import datetime
from domain.models import db

class Event(db.Model):
    __tablename__ = 'event'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=True)
    is_scan = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<Event {self.id}: {self.title}>'

    @property
    def client_name(self):
        return self.client.full_name if self.client else None
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'event_date': self.event_date,
            'client_id': self.client_id,
            'client_name': self.client_name,
            'is_scan': self.is_scan,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }