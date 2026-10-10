from datetime import datetime
from enum import Enum
import uuid

# Import db from credential_app
# This import will work because credential_app defines db before importing models
from credential_app import db

class Role(db.Model):
    """User roles in the system"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    """Base user model for all types of users"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    
    # Common fields
    is_verified = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    verification_token = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Student specific fields
    date_of_birth = db.Column(db.Date)
    roll_number = db.Column(db.String(50))
    college_name = db.Column(db.String(200))
    course = db.Column(db.String(100))
    year_of_study = db.Column(db.String(50))
    
    # College specific fields
    college_code = db.Column(db.String(50))
    address = db.Column(db.Text)
    university = db.Column(db.String(200))
    admin_name = db.Column(db.String(200))
    
    # Government specific fields
    department_name = db.Column(db.String(200))
    designation = db.Column(db.String(100))
    employee_id = db.Column(db.String(50))
    
    # Employer specific fields
    company_name = db.Column(db.String(200))
    company_registration = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    hr_contact = db.Column(db.String(200))
    
    # Relationships
    uploaded_documents = db.relationship('Document', backref='uploader', lazy=True, foreign_keys='Document.uploaded_by')
    verified_documents = db.relationship('Document', backref='verifier', lazy=True, foreign_keys='Document.verified_by')

class Document(db.Model):
    """Document model for uploaded certificates/marksheets"""
    __tablename__ = 'documents'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # marksheet, certificate, etc.
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    description = db.Column(db.Text)
    
    # OCR extracted data
    ocr_data = db.Column(db.JSON)
    extracted_text = db.Column(db.Text)
    
    # Verification status
    status = db.Column(db.String(50), default='pending')  # pending, verified, rejected
    verification_notes = db.Column(db.Text)
    verification_date = db.Column(db.DateTime)
    
    # Relationships
    uploaded_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    verified_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class College(db.Model):
    """College information model"""
    __tablename__ = 'colleges'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=False)
    university = db.Column(db.String(200), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    contact_phone = db.Column(db.String(15), nullable=False)
    
    # Status
    is_approved = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VerificationRequest(db.Model):
    """Verification requests for documents"""
    __tablename__ = 'verification_requests'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = db.Column(db.String(36), db.ForeignKey('documents.id'), nullable=False)
    requested_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    assigned_to = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    status = db.Column(db.String(50), default='pending')  # pending, in_progress, completed, rejected
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    document = db.relationship('Document', backref='verification_requests')
    requester = db.relationship('User', foreign_keys=[requested_by], backref='requested_verifications')
    assignee = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_verifications')

class AuditLog(db.Model):
    """Audit log for tracking all actions in the system"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)  # login, upload, verify, etc.
    resource_type = db.Column(db.String(50))  # document, user, etc.
    resource_id = db.Column(db.String(36))
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='audit_logs')

class SharedCredential(db.Model):
    """Shared credentials for external verification"""
    __tablename__ = 'shared_credentials'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = db.Column(db.String(36), db.ForeignKey('documents.id'), nullable=False)
    shared_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    share_token = db.Column(db.String(100), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    access_count = db.Column(db.Integer, default=0)
    max_access_count = db.Column(db.Integer, default=10)
    
    # Optional recipient info
    recipient_email = db.Column(db.String(120))
    recipient_name = db.Column(db.String(200))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    document = db.relationship('Document', backref='shared_credentials')
    sharer = db.relationship('User', backref='shared_credentials')