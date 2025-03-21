from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# Table client
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    telephone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)   # don't forget to put email uniqu=true after testing
    reason = db.Column(db.Text, nullable=False)
    previous_conditions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    scans = db.relationship('Scan', backref='client', lazy=True)
    events = db.relationship('Event', backref='client', lazy=True)

# Table scan
class Scan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    scan_date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    scan_reason = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<Scan {self.id} for Client {self.client_id}>'

    @property
    def client_full_name(self):
        return f'{self.client.first_name} {self.client.last_name}'
    
    @property
    def client_age(self):
        return f'{self.client.age}'
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_full_name': self.client_full_name,
            'scan_date': self.scan_date,
            'client_age': self.client_age,
            'scan_reason': self.scan_reason,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    

# Table events
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=True)  # Optional client relation
    is_scan = db.Column(db.Boolean, default=False)  # Whether this is a scan appointment
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<Event {self.id}: {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'event_date': self.event_date,
            'client_id': self.client_id,
            'client_name': self.client.first_name + ' ' + self.client.last_name if self.client else None,
            'is_scan': self.is_scan,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
