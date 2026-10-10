#!/usr/bin/env python3
"""
Simple Flask app starter without external dependencies for testing
"""

import os
import sys

# Try to import Flask, if not available, provide instructions
try:
    from flask import Flask, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    print("❌ Flask not installed!")
    print("📋 Please run: pip install flask flask-cors")
    sys.exit(1)

# Try to import CORS, if not available, continue without it
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    print("⚠️ flask-cors not installed - CORS may not work")
    CORS_AVAILABLE = False

app = Flask(__name__)

# Configure CORS if available
if CORS_AVAILABLE:
    CORS(app, origins=['http://localhost:3000'])
else:
    # Manual CORS headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

@app.route('/')
def home():
    return jsonify({'message': 'New India Credential Kavach API', 'status': 'running'})

@app.route('/api/documents', methods=['GET'])
def get_documents():
    return jsonify({'documents': [], 'message': 'Test endpoint working'})

@app.route('/api/documents/upload', methods=['POST'])
def upload_document():
    return jsonify({'message': 'Upload endpoint working', 'test': True})

@app.route('/api/auth/login', methods=['POST'])
def login():
    return jsonify({'message': 'Login endpoint working', 'test': True})

if __name__ == '__main__':
    print("🚀 Starting Simple Test Server...")
    print("📍 Server will run on: http://localhost:5001")
    print("🌐 CORS enabled for: http://localhost:3000")
    app.run(host='127.0.0.1', port=5001, debug=True)