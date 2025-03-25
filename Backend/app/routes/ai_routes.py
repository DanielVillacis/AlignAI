from flask import Blueprint, jsonify
from ..services.ai_service import AIService

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/run-script', methods=['GET'])
def run_script():
    try:
        AIService.run_model()
        return jsonify({'message': 'Model script launched successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500