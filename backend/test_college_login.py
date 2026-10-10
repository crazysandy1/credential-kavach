#!/usr/bin/env python3
"""
Test script to verify college login functionality
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock the Flask dependencies for testing
class MockJWTManager:
    pass

class MockCORS:
    def init_app(self, app, origins=None):
        pass

class MockMail:
    pass

# Monkey patch the imports
sys.modules['flask_jwt_extended'] = type(sys)('flask_jwt_extended')
sys.modules['flask_jwt_extended'].JWTManager = MockJWTManager
sys.modules['flask_cors'] = type(sys)('flask_cors')
sys.modules['flask_cors'].CORS = MockCORS
sys.modules['flask_mail'] = type(sys)('flask_mail')
sys.modules['flask_mail'].Mail = MockMail

from credential_app import create_app, db
from models import User
from werkzeug.security import check_password_hash

def test_college_login():
    """Test college login functionality"""
    app = create_app()

    with app.app_context():
        try:
            # Test college login
            college_email = 'college@test.com'
            college_password = 'College@123'

            print("=" * 60)
            print("🧪 TESTING COLLEGE LOGIN FUNCTIONALITY")
            print("=" * 60)

            # Find college user
            user = User.query.filter_by(email=college_email).first()

            if not user:
                print(f"❌ College user {college_email} not found")
                return False

            print(f"✅ Found college user: {user.email}")
            print(f"   Role: {user.role}")
            print(f"   Is Approved: {user.is_approved}")
            print(f"   Is Verified: {user.is_verified}")
            print(f"   Is Active: {user.is_active}")

            # Check password
            if not check_password_hash(user.password_hash, college_password):
                print("❌ Password verification failed")
                return False

            print("✅ Password verification successful")

            # Check approval status
            if not user.is_active:
                print("❌ Account is deactivated")
                return False

            if not user.is_verified:
                print("❌ Account is not verified")
                return False

            if user.role in ['college', 'government'] and not user.is_approved:
                print("❌ Account pending approval")
                return False

            print("✅ All login checks passed!")
            print("🎉 College login should work successfully")
            print(f"   Email: {college_email}")
            print(f"   Password: {college_password}")

            return True

        except Exception as e:
            print(f"❌ Error during college login test: {e}")
            return False

if __name__ == '__main__':
    success = test_college_login()
    if success:
        print("\n✅ COLLEGE LOGIN TEST PASSED")
    else:
        print("\n❌ COLLEGE LOGIN TEST FAILED")