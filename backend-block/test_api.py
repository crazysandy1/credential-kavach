#!/usr/bin/env python3
"""
Test script for the SIH Certificate Verification API
Run this to test the basic functionality
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_api():
    print("🚀 Testing SIH Certificate Verification API")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 2: API Info
    print("\n2. Testing API Info...")
    response = requests.get(f"{BASE_URL}/info/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test 3: Register a College User
    print("\n3. Testing College Registration...")
    college_data = {
        "username": "test_college",
        "email": "college@test.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "user_type": "college",
        "organization_name": "Test University",
        "contact_email": "contact@test.com",
        "first_name": "Test",
        "last_name": "College"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=college_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        college_tokens = response.json()['tokens']
        print("✅ College registered successfully!")
        print(f"Access Token: {college_tokens['access'][:20]}...")
    else:
        print(f"❌ Error: {response.json()}")
        college_tokens = None
    
    # Test 4: Register a Company User
    print("\n4. Testing Company Registration...")
    company_data = {
        "username": "test_company",
        "email": "company@test.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "user_type": "company",
        "organization_name": "Test Corp",
        "contact_email": "hr@test.com",
        "first_name": "Test",
        "last_name": "Company"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=company_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        company_tokens = response.json()['tokens']
        print("✅ Company registered successfully!")
        print(f"Access Token: {company_tokens['access'][:20]}...")
    else:
        print(f"❌ Error: {response.json()}")
        company_tokens = None
    
    # Test 5: Login Test
    print("\n5. Testing Login...")
    login_data = {
        "username": "test_college",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Login successful!")
    else:
        print(f"❌ Login failed: {response.json()}")
    
    # Test 6: Test Hash Check
    print("\n6. Testing Hash Check...")
    hash_data = {
        "file_hash": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    }
    
    response = requests.post(f"{BASE_URL}/certificates/check-hash/", json=hash_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 7: Dashboard Stats (if tokens are available)
    if college_tokens:
        print("\n7. Testing College Dashboard...")
        headers = {"Authorization": f"Bearer {college_tokens['access']}"}
        response = requests.get(f"{BASE_URL}/dashboard/stats/", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    
    if company_tokens:
        print("\n8. Testing Company Dashboard...")
        headers = {"Authorization": f"Bearer {company_tokens['access']}"}
        response = requests.get(f"{BASE_URL}/dashboard/stats/", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    
    print("\n" + "=" * 50)
    print("🎉 API Testing Complete!")
    print("\n📋 Available Endpoints:")
    print("• Swagger UI: http://127.0.0.1:8000/swagger/")
    print("• ReDoc: http://127.0.0.1:8000/redoc/")
    print("• Admin Panel: http://127.0.0.1:8000/admin/")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the API. Make sure the server is running:")
        print("   pipenv run python manage.py runserver")
