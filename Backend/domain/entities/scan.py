from datetime import datetime
from domain.models import db

class Scan(db.Model):
    __tablename__ = 'scan'
    
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
        return self.client.full_name
    
    @property
    def client_age(self):
        return str(self.client.age)
    
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