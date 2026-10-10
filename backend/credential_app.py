import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from datetime import timedelta

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
mail = Mail()

def create_app():
    """Application factory pattern for creating Flask app"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///credential_kavach.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-string')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # Mail configuration
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@credentialkavach.gov.in')
    
    # File upload configuration
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, origins=['http://localhost:3000', 'http://127.0.0.1:5500', 'file://'])
    mail.init_app(app)
    
    # Import and register blueprints
    from routes.auth import auth_bp
    from routes.api import api_bp
    from routes.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default government admin if not exists
        from models import User, Role
        admin_role = Role.query.filter_by(name='government').first()
        if not admin_role:
            # Create default roles
            roles = ['student', 'college', 'government', 'employer']
            for role_name in roles:
                role = Role(name=role_name)
                db.session.add(role)
            
            # Create default government admin
            from werkzeug.security import generate_password_hash
            import uuid
            
            admin_user = User(
                id=str(uuid.uuid4()),
                email='admin@credentialkavach.gov.in',
                password_hash=generate_password_hash(os.environ.get('ADMIN_PASSWORD', 'Admin@123')),
                full_name='System Administrator',
                phone='9999999999',
                role='government',
                is_verified=True,
                is_approved=True,
                is_active=True,
                department_name='Department of Higher Education, Jharkhand',
                designation='System Administrator',
                employee_id='GOV001'
            )
            db.session.add(admin_user)
            db.session.commit()
        
        # Ensure admin account exists and is properly configured
        admin_user = User.query.filter_by(email='admin@credentialkavach.gov.in').first()
        if admin_user:
            # Ensure admin account is always approved and active
            if not admin_user.is_approved or not admin_user.is_verified or not admin_user.is_active:
                admin_user.is_approved = True
                admin_user.is_verified = True
                admin_user.is_active = True
                db.session.commit()
                print("Admin account status verified and updated")
        else:
            # Create admin account if it doesn't exist
            from werkzeug.security import generate_password_hash
            import uuid
            
            admin_user = User(
                id=str(uuid.uuid4()),
                email='admin@credentialkavach.gov.in',
                password_hash=generate_password_hash(os.environ.get('ADMIN_PASSWORD', 'Admin@123')),
                full_name='System Administrator',
                phone='9999999999',
                role='government',
                is_verified=True,
                is_approved=True,
                is_active=True,
                department_name='Department of Higher Education, Jharkhand',
                designation='System Administrator',
                employee_id='GOV001'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin account created during app initialization")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)