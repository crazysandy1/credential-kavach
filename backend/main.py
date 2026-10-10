#!/usr/bin/env python3
"""
New India Credential Kavach - Flask Application Runner
Government of Jharkhand Digital Credential Verification Platform
"""

import os
from dotenv import load_dotenv
from credential_app import create_app

# Load environment variables
load_dotenv()

# Create Flask app
app = create_app()

if __name__ == '__main__':
    # Development configuration
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.environ.get('PORT', 5001))
    host = os.environ.get('HOST', '127.0.0.1')
    
    print("=" * 60)
    print("🛡️ NEW INDIA CREDENTIAL KAVACH")
    print("Government of Jharkhand")
    print("=" * 60)
    print(f"🌐 Server running on: http://{host}:{port}")
    print(f"🔧 Debug mode: {'ON' if debug_mode else 'OFF'}")
    print(f"📁 Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///credential_kavach.db')}")
    print("=" * 60)
    print("📋 API Endpoints:")
    print("   POST /api/auth/signup - User registration")
    print("   POST /api/auth/login - User login")
    print("   GET  /api/auth/profile - Get user profile")
    print("   POST /api/documents/upload - Upload document")
    print("   GET  /api/documents - Get user documents")
    print("   POST /api/documents/<id>/verify - Verify document")
    print("   GET  /api/admin/users - Get all users (gov only)")
    print("   POST /api/admin/users/<id>/approve - Approve user (gov only)")
    print("=" * 60)
    print("🚀 Starting server...")
    
    app.run(host=host, port=port, debug=debug_mode, threaded=True)