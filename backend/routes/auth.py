from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db, AuditLog
from datetime import datetime, timedelta
import uuid
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate Indian phone number"""
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, phone) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True

def log_user_action(user_id, action, details=None, resource_type=None, resource_id=None):
    """Log user actions for audit trail"""
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        print(f"Error logging user action: {e}")

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        # Validate email format
        if not validate_email(data['email']):
            return jsonify({'message': 'Invalid email format'}), 400
        
        # Validate phone number if provided
        if data.get('phone') and not validate_phone(data['phone']):
            return jsonify({'message': 'Invalid phone number format'}), 400
        
        # Validate password strength
        if not validate_password(data['password']):
            return jsonify({'message': 'Password must be at least 8 characters with uppercase, lowercase, and number'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already registered'}), 400
        
        # Validate role
        if data['role'] not in ['student', 'college', 'employer']:
            return jsonify({'message': 'Invalid role'}), 400
        
        # Create user based on role
        user_data = {
            'id': str(uuid.uuid4()),
            'email': data['email'],
            'password_hash': generate_password_hash(data['password']),
            'full_name': data.get('name', ''),
            'phone': data.get('phone', ''),
            'role': data['role'],
            'verification_token': str(uuid.uuid4()),
            'is_verified': True,  # Skip email verification for demo
            'is_approved': True if data['role'] in ['student', 'employer'] else False  # Auto-approve students and employers
        }
        
        # Role-specific fields
        if data['role'] == 'student':
            user_data.update({
                'roll_number': data.get('enrollment_number', ''),
                'college_name': data.get('institution', ''),
                'course': data.get('program', ''),
                'year_of_study': data.get('semester', '')
            })
            
        elif data['role'] == 'college':
            user_data.update({
                'college_name': data.get('college_name', ''),
                'college_code': data.get('registration_number', ''),
                'address': data.get('address', ''),
                'university': data.get('affiliation', ''),
                'admin_name': data.get('contact_person', ''),
                'designation': data.get('designation', '')
            })
            
        elif data['role'] == 'employer':
            user_data.update({
                'company_name': data.get('company_name', ''),
                'company_registration': data.get('company_registration', ''),
                'industry': data.get('industry', ''),
                'hr_contact': data.get('hr_contact', ''),
                'address': data.get('address', '')
            })
        
        # Create user
        user = User(**user_data)
        db.session.add(user)
        db.session.commit()
        
        # Log registration
        log_user_action(user.id, 'register', {'role': data['role']})
        
        return jsonify({
            'message': 'Registration successful! Please check your email for verification.',
            'user_id': user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Registration failed', 'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        # Special validation for government admin account
        if email == 'admin@credentialkavach.gov.in':
            print(f"Admin login attempt for: {email}")
            if password != 'Admin@123':
                print("Invalid admin password")
                return jsonify({'message': 'Invalid admin credentials'}), 401
            # If admin account doesn't exist in database, create it
            if not user:
                try:
                    from werkzeug.security import generate_password_hash
                    user = User(
                        email='admin@credentialkavach.gov.in',
                        password_hash=generate_password_hash('Admin@123'),
                        full_name='Government Administrator',
                        phone='9999999999',
                        role='government',
                        department_name='Ministry of Education',
                        designation='System Administrator',
                        employee_id='GOV001',
                        is_verified=True,
                        is_approved=True,
                        is_active=True
                    )
                    db.session.add(user)
                    db.session.commit()
                    print(f"Admin account created successfully: {user.email}")
                except Exception as e:
                    db.session.rollback()
                    print(f"Error creating admin account: {e}")
                    return jsonify({'message': 'Error creating admin account'}), 500
            else:
                print(f"Admin account exists: {user.email}, is_approved: {user.is_approved}")
                # If admin account exists but is not approved, approve it
                if not user.is_approved:
                    try:
                        user.is_approved = True
                        user.is_verified = True
                        user.is_active = True
                        db.session.commit()
                        print(f"Admin account approved: {user.email}")
                    except Exception as e:
                        db.session.rollback()
                        print(f"Error approving admin account: {e}")
                        return jsonify({'message': 'Error approving admin account'}), 500
        else:
            if not user or not check_password_hash(user.password_hash, password):
                return jsonify({'message': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'message': 'Account is deactivated'}), 401
        
        if not user.is_verified:
            return jsonify({'message': 'Please verify your email before logging in'}), 401
        
        # Restrict government access to only the designated admin account
        if user.role == 'government' and user.email != 'admin@credentialkavach.gov.in':
            return jsonify({'message': 'Unauthorized government access'}), 403
        
        # Skip approval check for the designated admin account
        if user.role in ['college', 'government', 'employer'] and not user.is_approved and user.email != 'admin@credentialkavach.gov.in':
            print(f"User {user.email} is pending approval")
            return jsonify({'message': 'Account pending approval from administrator'}), 401
        
        print(f"User {user.email} passed all checks, proceeding with login")
        
        # Create tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={'role': user.role}
        )
        refresh_token = create_refresh_token(identity=user.id)
        
        # Log successful login
        log_user_action(user.id, 'login')
        
        # Prepare user data (exclude sensitive information)
        user_data = {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'phone': user.phone,
            'role': user.role,
            'is_verified': user.is_verified,
            'is_approved': user.is_approved,
            'created_at': user.created_at.isoformat()
        }
        
        # Add role-specific data
        if user.role == 'student':
            user_data.update({
                'roll_number': user.roll_number,
                'college_name': user.college_name,
                'course': user.course,
                'year_of_study': user.year_of_study
            })
        elif user.role == 'college':
            user_data.update({
                'college_name': user.college_name,
                'college_code': user.college_code,
                'university': user.university,
                'admin_name': user.admin_name
            })
        elif user.role == 'government':
            user_data.update({
                'department_name': user.department_name,
                'designation': user.designation,
                'employee_id': user.employee_id
            })
        elif user.role == 'employer':
            user_data.update({
                'company_name': user.company_name,
                'company_registration': user.company_registration,
                'industry': user.industry,
                'hr_contact': user.hr_contact
            })
        
        return jsonify({
            'message': 'Login successful',
            'token': access_token,
            'refresh_token': refresh_token,
            'user': user_data
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Login failed', 'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'message': 'Invalid user'}), 401
        
        new_token = create_access_token(
            identity=current_user_id,
            additional_claims={'role': user.role}
        )
        
        return jsonify({'token': new_token}), 200
        
    except Exception as e:
        return jsonify({'message': 'Token refresh failed', 'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Prepare user data
        user_data = {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'phone': user.phone,
            'role': user.role,
            'is_verified': user.is_verified,
            'is_approved': user.is_approved,
            'created_at': user.created_at.isoformat()
        }
        
        # Add role-specific data
        if user.role == 'student':
            user_data.update({
                'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
                'roll_number': user.roll_number,
                'college_name': user.college_name,
                'course': user.course,
                'year_of_study': user.year_of_study
            })
        elif user.role == 'college':
            user_data.update({
                'college_name': user.college_name,
                'college_code': user.college_code,
                'address': user.address,
                'university': user.university,
                'admin_name': user.admin_name
            })
        elif user.role == 'government':
            user_data.update({
                'department_name': user.department_name,
                'designation': user.designation,
                'employee_id': user.employee_id
            })
        
        return jsonify({'user': user_data}), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get profile', 'error': str(e)}), 500

@auth_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """Verify user email with token"""
    try:
        user = User.query.filter_by(verification_token=token).first()
        
        if not user:
            return jsonify({'message': 'Invalid verification token'}), 400
        
        if user.is_verified:
            return jsonify({'message': 'Email already verified'}), 200
        
        user.is_verified = True
        user.verification_token = None
        db.session.commit()
        
        # Log email verification
        log_user_action(user.id, 'email_verified')
        
        return jsonify({'message': 'Email verified successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Email verification failed', 'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client-side token removal)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Log logout action
        log_user_action(current_user_id, 'logout')
        
        return jsonify({'message': 'Logout successful'}), 200
        
    except Exception as e:
        return jsonify({'message': 'Logout failed', 'error': str(e)}), 500