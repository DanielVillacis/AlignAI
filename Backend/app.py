from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Client, Scan, Event
from datetime import datetime, timedelta
import subprocess

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alignai.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)
migrate = Migrate(app, db)

# Create tables
with app.app_context():
    db.create_all()

"""
Routes for the API, this file can and will be refactored to a more organized structure later on
"""

# CRUD Endpoints
# ---------------- Client Endpoints ----------------
# Create a new client
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
    

# Get all clients
@app.route('/api/clients', methods=['GET'])
def get_clients():
    clients = db.session.query(Client).all()
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


# Get a single client by its ID
@app.route('/api/clients/<int:id>', methods=['GET'])
def get_client(id):
    client = db.session.query(Client).get_or_404(id)
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


# Update a client by its ID
@app.route('/api/clients/<int:id>', methods=['PUT'])
def update_client(id):
    client = db.session.query(Client).get_or_404(id)
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


# Delete a client by its ID
@app.route('/api/clients/<int:id>', methods=['DELETE'])
def delete_client(id):
    client = db.session.query(Client).get_or_404(id)
    try:
        db.session.delete(client)
        db.session.commit()
        return jsonify({'message': 'Client deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    

# ---------------- Scan Endpoints ----------------
@app.route('/api/scans', methods=['POST'])
def create_scan():
    data = request.json
    new_scan = Scan(
        client_id=data['client_id'],
        scan_reason=data['scan_reason']
    )
    db.session.add(new_scan)
    try:
        db.session.commit()
        return jsonify({'message': 'Scan created successfully', 'id': new_scan.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    

@app.route('/api/scans', methods=['GET'])
def get_scans():
    scans = Scan.query.all()
    return jsonify([scan.to_dict() for scan in scans])


@app.route('/api/scans/<int:id>', methods=['GET'])
def get_scan(id):
    scan = Scan.query.get_or_404(id)
    return jsonify(scan.to_dict())


# delete a scan by its ID
@app.route('/api/scans/<int:id>', methods=['DELETE'])
def delete_scan(id):
    scan = Scan.query.get_or_404(id)
    try:
        db.session.delete(scan)
        db.session.commit()
        return jsonify({'message': 'Scan deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# ---------------- Event Endpoints ----------------
@app.route('/api/events', methods=['POST'])
def create_event():
    data = request.json
    new_event = Event(
        title=data['title'],
        description=data.get('description', ''),
        event_date=datetime.fromisoformat(data['event_date']),
        client_id=data.get('client_id'),  # Optional
        is_scan=data.get('is_scan', False)
    )
    db.session.add(new_event)
    try:
        db.session.commit()
        return jsonify({'message': 'Event created successfully', 'id': new_event.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@app.route('/api/events', methods=['GET'])
def get_events():
    # Get events for a specific date if provided
    date_str = request.args.get('date')
    if date_str:
        try:
            # Parse the date string
            target_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            # Get all events for that day
            start_of_day = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
            end_of_day = start_of_day + timedelta(days=1)
            
            events = Event.query.filter(
                Event.event_date >= start_of_day,
                Event.event_date < end_of_day
            ).all()
            
            return jsonify([event.to_dict() for event in events])
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
    else:
        # Return all events
        events = Event.query.all()
        return jsonify([event.to_dict() for event in events])


@app.route('/api/events/<int:id>', methods=['GET'])
def get_event(id):
    event = Event.query.get_or_404(id)
    return jsonify(event.to_dict())


@app.route('/api/events/<int:id>', methods=['PUT'])
def update_event(id):
    event = Event.query.get_or_404(id)
    data = request.json
    
    if 'title' in data:
        event.title = data['title']
    if 'description' in data:
        event.description = data['description']
    if 'event_date' in data:
        event.event_date = datetime.fromisoformat(data['event_date'])
    if 'client_id' in data:
        event.client_id = data['client_id']
    if 'is_scan' in data:
        event.is_scan = data['is_scan']
    
    try:
        db.session.commit()
        return jsonify({'message': 'Event updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@app.route('/api/events/<int:id>', methods=['DELETE'])
def delete_event(id):
    event = Event.query.get_or_404(id)
    try:
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'Event deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# ---------------- AI Model Endpoints ----------------
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