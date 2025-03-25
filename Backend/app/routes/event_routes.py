from flask import Blueprint, request, jsonify
from ..services.event_services import EventService

event_bp = Blueprint('event', __name__)

@event_bp.route('', methods=['POST'])
def create_event():
    try:
        new_event = EventService.create_event(request.json)
        return jsonify({'message': 'Event created successfully', 'id': new_event.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@event_bp.route('', methods=['GET'])
def get_events():
    date_str = request.args.get('date')
    try:
        if date_str:
            events = EventService.get_events_by_date(date_str)
        else:
            events = EventService.get_all_events()
        return jsonify([event.to_dict() for event in events])
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

@event_bp.route('/<int:id>', methods=['GET'])
def get_event(id):
    event = EventService.get_event_by_id(id)
    return jsonify(event.to_dict())

@event_bp.route('/<int:id>', methods=['PUT'])
def update_event(id):
    try:
        event = EventService.get_event_by_id(id)
        updated_event = EventService.update_event(event, request.json)
        return jsonify({'message': 'Event updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@event_bp.route('/<int:id>', methods=['DELETE'])
def delete_event(id):
    try:
        event = EventService.get_event_by_id(id)
        EventService.delete_event(event)
        return jsonify({'message': 'Event deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400