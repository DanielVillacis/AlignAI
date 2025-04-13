from flask import Blueprint, jsonify, request
from ..services.ai_service import AIService

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/run-script', methods=['POST'])
def run_script():
    try:
        data = request.json

        if not data or not data.get('client_id'):
            return jsonify({'error' : 'Client ID is required'}), 400
        
        try:
            client_id = int(data.get('client_id'))
        except (ValueError, TypeError):
            return jsonify({'error': 'Client ID must be an integer'}), 400
        
        scan_reason = data.get('scan_reason', 'Consult')

        result = AIService.run_model(client_id, scan_reason)

        return jsonify({'message': 'Scan started for client', 'client_id': client_id}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500