from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Client
import subprocess

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alignai.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

"""
Routes for the API, this file can and will be refactored to a more organized structure later on
"""

# CRUD Endpoints
@app.route('/api/clients', methods=['POST'])
def create_client():
    data = request.json
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
    try:
        db.session.commit()
        return jsonify({'message': 'Client created successfully', 'id': new_client.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    

@app.route('/api/clients', methods=['GET'])
def get_clients():
    clients = Client.query.all()
    return jsonify([{
        'id': client.id,
        'first_name': client.first_name,
        'last_name': client.last_name,
        'age': client.age,
        'gender': client.gender,
        'telephone': client.telephone,
        'email': client.email,
        'reason': client.reason,
        'previous_conditions': client.previous_conditions
    } for client in clients])


@app.route('/api/clients/<int:id>', methods=['GET'])
def get_client(id):
    client = Client.query.get_or_404(id)
    return jsonify({
        'id': client.id,
        'first_name': client.first_name,
        'last_name': client.last_name,
        'age': client.age,
        'gender': client.gender,
        'telephone': client.telephone,
        'email': client.email,
        'reason': client.reason,
        'previous_conditions': client.previous_conditions
    })


@app.route('/api/clients/<int:id>', methods=['PUT'])
def update_client(id):
    client = Client.query.get_or_404(id)
    data = request.json
    
    client.first_name = data.get('first_name', client.first_name)
    client.last_name = data.get('last_name', client.last_name)
    client.age = data.get('age', client.age)
    client.gender = data.get('gender', client.gender)
    client.telephone = data.get('telephone', client.telephone)
    client.email = data.get('email', client.email)
    client.reason = data.get('reason', client.reason)
    client.previous_conditions = data.get('previous_conditions', client.previous_conditions)
    
    try:
        db.session.commit()
        return jsonify({'message': 'Client updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@app.route('/api/clients/<int:id>', methods=['DELETE'])
def delete_client(id):
    client = Client.query.get_or_404(id)
    try:
        db.session.delete(client)
        db.session.commit()
        return jsonify({'message': 'Client deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# Route to run the model.py script
@app.route('/run-script', methods=['GET'])
def run_script():
    try:
        # Start the model script as a separate process
        subprocess.Popen(['python3', 'test.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return jsonify({'message': 'Model script launched successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)