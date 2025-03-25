from datetime import datetime
from domain.models import db

class Client(db.Model):
    __tablename__ = 'client'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    telephone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    previous_conditions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    scans = db.relationship('Scan', backref='client', lazy=True)
    events = db.relationship('Event', backref='client', lazy=True)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'age': self.age,
            'gender': self.gender,
            'telephone': self.telephone,
            'email': self.email,
            'reason': self.reason,
            'previous_conditions': self.previous_conditions,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }