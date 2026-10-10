#!/usr/bin/env python3
"""
Script to create an employer user for testing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from credential_app import create_app
from models import User
from werkzeug.security import generate_password_hash
import uuid

def create_employer_user():
    """Create a test employer user"""

    # Employer details
    employer_data = {
        'email': 'employer@test.com',
        'password': 'password123',
        'full_name': 'John Smith',
        'phone': '+1-555-0123',
        'role': 'employer',
        'company_name': 'Tech Solutions Inc.',
        'company_registration': 'REG123456',
        'industry': 'Technology',
        'hr_contact': 'hr@techsolutions.com'
    }

    app = create_app()

    with app.app_context():
        # Check if employer already exists
        existing_user = User.query.filter_by(email=employer_data['email']).first()
        if existing_user:
            print(f"Employer user already exists: {employer_data['email']}")
            print(f"Login credentials:")
            print(f"Email: {employer_data['email']}")
            print(f"Password: {employer_data['password']}")
            return

        # Create new employer user
        employer = User(
            id=str(uuid.uuid4()),
            email=employer_data['email'],
            password_hash=generate_password_hash(employer_data['password']),
            full_name=employer_data['full_name'],
            phone=employer_data['phone'],
            role=employer_data['role'],
            company_name=employer_data['company_name'],
            company_registration=employer_data['company_registration'],
            industry=employer_data['industry'],
            hr_contact=employer_data['hr_contact'],
            is_verified=True,
            is_approved=True,  # Auto-approve for testing
            is_active=True
        )

        try:
            from credential_app import db
            db.session.add(employer)
            db.session.commit()

            print("✅ Employer user created successfully!")
            print("\n" + "="*50)
            print("EMPLOYER LOGIN CREDENTIALS:")
            print("="*50)
            print(f"Email: {employer_data['email']}")
            print(f"Password: {employer_data['password']}")
            print(f"Company: {employer_data['company_name']}")
            print(f"Role: {employer_data['role']}")
            print("="*50)
            print("\nYou can now login with these credentials!")

        except Exception as e:
            print(f"❌ Error creating employer user: {e}")
            db.session.rollback()

if __name__ == "__main__":
    print("Creating test employer user...")
    create_employer_user()