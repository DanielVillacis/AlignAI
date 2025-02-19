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
