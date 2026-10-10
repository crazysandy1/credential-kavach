#!/usr/bin/env python3
"""
Test script to create and approve a college account for testing
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from credential_app import create_app, db
from models import User
from werkzeug.security import generate_password_hash

def create_test_college_account():
    """Create a test college account that is approved and ready for login"""
    app = create_app()

    with app.app_context():
        try:
            # Check if test college account already exists
            college_user = User.query.filter_by(email='college@test.com').first()

            if college_user:
                print(f"Test college account already exists: {college_user.email}")
                print(f"Is approved: {college_user.is_approved}")
                print(f"Is verified: {college_user.is_verified}")
                print(f"Is active: {college_user.is_active}")

                # Ensure it's approved and active
                if not college_user.is_approved or not college_user.is_verified or not college_user.is_active:
                    college_user.is_approved = True
                    college_user.is_verified = True
                    college_user.is_active = True
                    db.session.commit()
                    print("Test college account updated and approved")
                else:
                    print("Test college account is already approved and active")
            else:
                print("Creating test college account...")

                # Create test college account
                college_user = User(
                    email='college@test.com',
                    password_hash=generate_password_hash('College@123'),
                    full_name='Test College Administrator',
                    phone='9876543210',
                    role='college',
                    college_name='Test Engineering College',
                    college_code='TEC001',
                    address='123 Test Street, Test City, Jharkhand',
                    university='Test University',
                    admin_name='Dr. Test Admin',
                    designation='Principal',
                    is_verified=True,
                    is_approved=True,
                    is_active=True
                )
                db.session.add(college_user)
                db.session.commit()
                print("Test college account created successfully!")
                print("Email: college@test.com")
                print("Password: College@123")

        except Exception as e:
            db.session.rollback()
            print(f"Error creating/updating college account: {e}")

if __name__ == '__main__':
    create_test_college_account()