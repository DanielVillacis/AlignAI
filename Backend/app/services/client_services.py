from domain.models import db
from domain.entities import Client

class ClientService:
    
    @staticmethod
    def create_client(data):
        new_client = Client(
            first_name=data['first_name'],
            last_name=data['last_name'],
            age=data['age'],
            gender=data['gender'],
            telephone=data['telephone'],
            email=data['email'],
            reason=data['reason'],
            previous_conditions=data.get('previous_conditions', '')
        )
        db.session.add(new_client)
        db.session.commit()
        return new_client

    @staticmethod
    def get_all_clients():
        return Client.query.all()

    @staticmethod
    def get_client_by_id(id):
        return Client.query.get_or_404(id)

    @staticmethod
    def update_client(client, data):
        client.first_name = data.get('first_name', client.first_name)
        client.last_name = data.get('last_name', client.last_name)
        client.age = data.get('age', client.age)
        client.gender = data.get('gender', client.gender)
        client.telephone = data.get('telephone', client.telephone)
        client.email = data.get('email', client.email)
        client.reason = data.get('reason', client.reason)
        client.previous_conditions = data.get('previous_conditions', client.previous_conditions)
        db.session.commit()
        return client

    @staticmethod
    def delete_client(client):
        db.session.delete(client)
        db.session.commit()