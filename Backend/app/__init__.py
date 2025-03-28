from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from domain.models import db
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    CORS(app)
    db.init_app(app)
    Migrate(app, db)
    
    # Register blueprints
    from .routes.client_routes import client_bp
    from .routes.scan_routes import scan_bp
    from .routes.event_routes import event_bp
    from .routes.ai_routes import ai_bp
    from .routes.authentication_routes import auth_bp
    
    app.register_blueprint(client_bp, url_prefix='/api/clients')
    app.register_blueprint(scan_bp, url_prefix='/api/scans')
    app.register_blueprint(event_bp, url_prefix='/api/events')
    app.register_blueprint(ai_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app