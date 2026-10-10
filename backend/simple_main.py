#!/usr/bin/env python3
"""
Lightweight server for testing authentication without OCR dependencies
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from credential_app import db
from routes.auth import auth_bp
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def create_simple_app():
    """Create Flask app without OCR dependencies"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///credential_kavach.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])
    JWTManager(app)
    
    # Initialize database
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints (only auth for now)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # Simple test endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'New India Credential Kavach - Authentication Server'
        })
    
    @app.route('/api/test')
    def test():
        return jsonify({
            'message': 'Server is working!',
            'endpoints': {
                'auth': '/api/auth/login, /api/auth/signup',
                'health': '/api/health'
            }
        })
    
    return app

if __name__ == '__main__':
    print("=" * 60)
    print("🛡️ NEW INDIA CREDENTIAL KAVACH - AUTH TEST SERVER")
    print("Government of Jharkhand")
    print("=" * 60)
    print("🌐 Server running on: http://127.0.0.1:5001")
    print("🔧 Debug mode: ON")
    print("📁 Database: sqlite:///credential_kavach.db")
    print("=" * 60)
    print("📋 Available Endpoints:")
    print("   POST /api/auth/signup - User registration")
    print("   POST /api/auth/login - User login")
    print("   GET  /api/health - Health check")
    print("   GET  /api/test - Test endpoint")
    print("=" * 60)
    print("🚀 Starting authentication server...")
    
    app = create_simple_app()
    app.run(host='127.0.0.1', port=5001, debug=True)