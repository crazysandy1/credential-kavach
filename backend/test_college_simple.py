#!/usr/bin/env python3
"""
Simple test to verify college account status in database
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up minimal database connection
os.environ['DATABASE_URL'] = 'sqlite:///credential_kavach.db'

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash

# Initialize SQLAlchemy
db = SQLAlchemy()

# Import models after db initialization
from models import User

def test_college_account():
    """Test college account status"""
    try:
        # Configure database
        db_uri = os.environ.get('DATABASE_URL', 'sqlite:///credential_kavach.db')
        print(f"Database URI: {db_uri}")

        # Create Flask app context manually
        from flask import Flask
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        db.init_app(app)

        with app.app_context():
            print("=" * 60)
            print("🧪 TESTING COLLEGE ACCOUNT STATUS")
            print("=" * 60)

            # Find college user
            college_user = User.query.filter_by(email='college@test.com').first()

            if not college_user:
                print("❌ College account not found")
                return False

            print(f"✅ Found college account: {college_user.email}")
            print(f"   Full Name: {college_user.full_name}")
            print(f"   Role: {college_user.role}")
            print(f"   College Name: {college_user.college_name}")
            print(f"   College Code: {college_user.college_code}")
            print(f"   Is Approved: {college_user.is_approved}")
            print(f"   Is Verified: {college_user.is_verified}")
            print(f"   Is Active: {college_user.is_active}")

            # Test password
            test_password = 'College@123'
            if check_password_hash(college_user.password_hash, test_password):
                print("✅ Password verification successful")
            else:
                print("❌ Password verification failed")
                return False

            # Check all login conditions
            if not college_user.is_active:
                print("❌ Account is deactivated")
                return False

            if not college_user.is_verified:
                print("❌ Account is not verified")
                return False

            if college_user.role in ['college', 'government'] and not college_user.is_approved:
                print("❌ Account pending approval")
                return False

            print("✅ All login conditions met!")
            print("\n🎉 COLLEGE LOGIN SHOULD WORK")
            print("   Email: college@test.com")
            print("   Password: College@123")
            print("   Expected Result: Successful login and redirect to college dashboard")

            return True

    except Exception as e:
        print(f"❌ Error testing college account: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_college_account()
    if success:
        print("\n✅ COLLEGE ACCOUNT TEST PASSED")
    else:
        print("\n❌ COLLEGE ACCOUNT TEST FAILED")