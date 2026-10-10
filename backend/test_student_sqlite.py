#!/usr/bin/env python3
"""
Direct SQLite test for student account
"""

import sqlite3
import os
from werkzeug.security import check_password_hash

def test_student_account_sqlite():
    """Test student account directly in SQLite database"""
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
        print("🧪 TESTING STUDENT ACCOUNT IN DATABASE")
        print("=" * 60)

        # Query student user
        cursor.execute("SELECT * FROM users WHERE email = ?", ('student@test.com',))
        user_row = cursor.fetchone()

        if not user_row:
            print("❌ Student account not found in database")
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
        roll_number = user_row[13] if len(user_row) > 13 else None  # roll_number field
        college_name = user_row[14] if len(user_row) > 14 else None  # college_name field

        print(f"✅ Found student account: {email}")
        print(f"   Full Name: {full_name}")
        print(f"   Role: {role}")
        print(f"   Roll Number: {roll_number}")
        print(f"   College Name: {college_name}")
        print(f"   Is Approved: {is_approved}")
        print(f"   Is Verified: {is_verified}")
        print(f"   Is Active: {is_active}")

        # Test multiple possible passwords
        test_passwords = ['Student@123', 'student123', 'Student123', 'test123', 'password']
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

        # For students, approval is typically not required, but check anyway
        if role == 'student' and not is_approved:
            print("⚠️ Student account is not approved (may not be required)")

        if password_matched:
            print("✅ All login conditions met!")
            print("\n🎉 STUDENT LOGIN SHOULD WORK")
            print("   Email: student@test.com")
            print("   Password: [Found working password]")
            print("   Expected Result: Successful login and redirect to student dashboard")
        else:
            print("❌ Password needs to be reset")

        conn.close()
        return password_matched

    except Exception as e:
        print(f"❌ Error testing student account: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_student_account_sqlite()
    if success:
        print("\n✅ STUDENT ACCOUNT TEST PASSED")
    else:
        print("\n❌ STUDENT ACCOUNT TEST FAILED")