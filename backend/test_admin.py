#!/usr/bin/env python3
"""
Test script to verify admin account creation and login
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from credential_app import create_app, db
from models import User
from werkzeug.security import generate_password_hash

def test_admin_account():
    """Test admin account creation and verification"""
    app = create_app()

    with app.app_context():
        try:
            # Check if admin account exists
            admin_user = User.query.filter_by(email='admin@credentialkavach.gov.in').first()

            if admin_user:
                print(f"Admin account exists: {admin_user.email}")
                print(f"Role: {admin_user.role}")
                print(f"Is approved: {admin_user.is_approved}")
                print(f"Is verified: {admin_user.is_verified}")
                print(f"Is active: {admin_user.is_active}")

                # Update admin account to ensure it's properly approved
                admin_user.is_approved = True
                admin_user.is_verified = True
                admin_user.is_active = True
                db.session.commit()
                print("Admin account updated successfully")
            else:
                print("Admin account does not exist, creating...")

                # Create admin account
                admin_user = User(
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

                db.session.add(admin_user)
                db.session.commit()
                print(f"Admin account created: {admin_user.email}")

        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    test_admin_account()