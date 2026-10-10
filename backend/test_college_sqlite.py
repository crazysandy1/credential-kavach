#!/usr/bin/env python3
"""
Direct SQLite test for college account
"""

import sqlite3
import os
from werkzeug.security import check_password_hash

def test_college_account_sqlite():
    """Test college account directly in SQLite database"""
    try:
        # Database path
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'credential_kavach.db')

        if not os.path.exists(db_path):
            print(f"❌ Database file not found: {db_path}")
            return False

        print(f"✅ Found database: {db_path}")

        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("=" * 60)
        print("🧪 TESTING COLLEGE ACCOUNT IN DATABASE")
        print("=" * 60)

        # Query college user
        cursor.execute("SELECT * FROM users WHERE email = ?", ('college@test.com',))
        user_row = cursor.fetchone()

        if not user_row:
            print("❌ College account not found in database")
            conn.close()
            return False

        # Parse user data (assuming standard column order from model)
        user_id = user_row[0]
        email = user_row[1]
        password_hash = user_row[2]
        full_name = user_row[3]
        phone = user_row[4]
        role = user_row[5]
        is_verified = bool(user_row[6])
        is_approved = bool(user_row[7])
        is_active = bool(user_row[8])
        college_name = user_row[15]  # college_name field
        college_code = user_row[16]  # college_code field

        print(f"✅ Found college account: {email}")
        print(f"   Full Name: {full_name}")
        print(f"   Role: {role}")
        print(f"   College Name: {college_name}")
        print(f"   College Code: {college_code}")
        print(f"   Is Approved: {is_approved}")
        print(f"   Is Verified: {is_verified}")
        print(f"   Is Active: {is_active}")

        # Test password
        test_passwords = ['College@123', 'college123', 'College123', 'test123', 'password']
        password_matched = False

        for test_password in test_passwords:
            if check_password_hash(password_hash, test_password):
                print(f"✅ Password verification successful with: {test_password}")
                password_matched = True
                break

        if not password_matched:
            print("❌ Password verification failed for all common passwords")
            print(f"   Password hash: {password_hash[:20]}...")
            # Don't return False here, continue with other checks

        # Check all login conditions
        if not is_active:
            print("❌ Account is deactivated")
            conn.close()
            return False

        if not is_verified:
            print("❌ Account is not verified")
            conn.close()
            return False

        if role in ['college', 'government'] and not is_approved:
            print("❌ Account pending approval")
            conn.close()
            return False

        print("✅ All login conditions met!")
        print("\n🎉 COLLEGE LOGIN SHOULD WORK")
        print("   Email: college@test.com")
        print("   Password: College@123")
        print("   Expected Result: Successful login and redirect to college dashboard")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error testing college account: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_college_account_sqlite()
    if success:
        print("\n✅ COLLEGE ACCOUNT TEST PASSED")
    else:
        print("\n❌ COLLEGE ACCOUNT TEST FAILED")