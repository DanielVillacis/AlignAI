from flask import Blueprint, request, jsonify
from ..services.client_services import ClientService

client_bp = Blueprint('client', __name__)

@client_bp.route('', methods=['POST'])
def create_client():
    try:
        new_client = ClientService.create_client(request.json)
        return jsonify({'message': 'Client created successfully', 'id': new_client.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@client_bp.route('', methods=['GET'])
def get_clients():
    clients = ClientService.get_all_clients()
    return jsonify([client.to_dict() for client in clients])

@client_bp.route('/<int:id>', methods=['GET'])
def get_client(id):
    client = ClientService.get_client_by_id(id)
    return jsonify(client.to_dict())

@client_bp.route('/<int:id>', methods=['PUT'])
def update_client(id):
    try:
        client = ClientService.get_client_by_id(id)
        updated_client = ClientService.update_client(client, request.json)
        return jsonify({'message': 'Client updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@client_bp.route('/<int:id>', methods=['DELETE'])
def delete_client(id):
    try:
        client = ClientService.get_client_by_id(id)
        ClientService.delete_client(client)
        return jsonify({'message': 'Client deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400