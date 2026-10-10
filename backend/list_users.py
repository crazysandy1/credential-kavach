#!/usr/bin/env python3
"""
Script to list all users in the database
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from credential_app import create_app, db
from models import User

def list_all_users():
    """List all users in the database"""
    app = create_app()

    with app.app_context():
        try:
            users = User.query.all()

            print("=" * 80)
            print("📋 ALL USERS IN DATABASE")
            print("=" * 80)

            if not users:
                print("No users found in database")
                return

            for user in users:
                print(f"ID: {user.id}")
                print(f"Email: {user.email}")
                print(f"Full Name: {user.full_name}")
                print(f"Role: {user.role}")
                print(f"Is Approved: {user.is_approved}")
                print(f"Is Verified: {user.is_verified}")
                print(f"Is Active: {user.is_active}")
                if user.role == 'college':
                    print(f"College Name: {user.college_name}")
                    print(f"College Code: {user.college_code}")
                elif user.role == 'government':
                    print(f"Department: {user.department_name}")
                    print(f"Designation: {user.designation}")
                print("-" * 40)

        except Exception as e:
            print(f"Error listing users: {e}")

if __name__ == '__main__':
    list_all_users()