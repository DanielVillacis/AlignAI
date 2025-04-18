from flask import Blueprint, request, jsonify
from ..services.authentication_service import AuthService
from functools import wraps

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400
        
    result, error = AuthService.register_user(data)
    
    if error:
        return jsonify({"error": error}), 400
        
    return jsonify(result), 201
    
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400
        
    result, error = AuthService.login_user(data.get('email'), data.get('password'))
    
    if error:
        return jsonify({"error": error}), 401
        
    return jsonify(result), 200
    
@auth_bp.route('/google', methods=['POST'])
def google_auth():
    data = request.get_json()
    
    if not data or not data.get('id_token'):
        return jsonify({"error": "Google ID token is required"}), 400
        
    result, error = AuthService.google_auth(data.get('id_token'))
    
    if error:
        return jsonify({"error": error}), 401
        
    return jsonify(result), 200
    
@auth_bp.route('/apple', methods=['POST'])
def apple_auth():
    data = request.get_json()
    
    if not data or not data.get('identity_token'):
        return jsonify({"error": "Apple identity token is required"}), 400
        
    result, error = AuthService.apple_auth(data.get('identity_token'))
    
    if error:
        return jsonify({"error": error}), 401
        
    return jsonify(result), 200
    
@auth_bp.route('/refresh-token', methods=['POST'])
def refresh_token():
    data = request.get_json()
    
    if not data or not data.get('refresh_token'):
        return jsonify({"error": "Refresh token is required"}), 400
        
    result, error = AuthService.refresh_auth_token(data.get('refresh_token'))
    
    if error:
        return jsonify({"error": error}), 401
        
    return jsonify(result), 200
    
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # get token from header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
        if not token:
            return jsonify({"error": "Token is missing"}), 401
            
        payload, error = AuthService.verify_token(token)
        
        if error:
            return jsonify({"error": error}), 401
            
        request.user_id = payload['sub']
        request.is_admin = payload.get('is_admin', False)
        
        return f(*args, **kwargs)
        
    return decorated