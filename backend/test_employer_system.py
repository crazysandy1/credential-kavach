#!/usr/bin/env python3
"""
Test script to verify employer role functionality
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_employer_signup():
    """Test employer signup"""
    print("Testing employer signup...")
    
    signup_data = {
        "email": "test.employer@company.com",
        "password": "password123",
        "confirm_password": "password123",
        "role": "employer",
        "company_name": "Test Corp",
        "company_address": "123 Business St, City, State",
        "contact_person": "John Doe",
        "phone": "+1-555-0123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/signup", json=signup_data)
        print(f"Signup Response: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 201
    except Exception as e:
        print(f"Signup failed: {e}")
        return False

def test_employer_login():
    """Test employer login"""
    print("\nTesting employer login...")
    
    login_data = {
        "email": "test.employer@company.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        print(f"Login Response: {response.status_code}")
        data = response.json()
        print(f"Response: {data}")
        
        if response.status_code == 200:
            return data.get('access_token')
        return None
    except Exception as e:
        print(f"Login failed: {e}")
        return None

def test_document_verification(token):
    """Test document verification endpoint"""
    print("\nTesting document verification...")
    
    headers = {"Authorization": f"Bearer {token}"}
    verification_data = {
        "document_id": "test_doc_123",
        "verification_status": "verified",
        "fraud_indicators": ["none"],
        "confidence_score": 95,
        "notes": "Document appears authentic"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/verify-document", 
                               json=verification_data, headers=headers)
        print(f"Verification Response: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Verification failed: {e}")
        return False

def test_documents_list():
    """Test public documents list endpoint"""
    print("\nTesting documents list endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/documents")
        print(f"Documents List Response: {response.status_code}")
        data = response.json()
        print(f"Response: {data}")
        return response.status_code == 200
    except Exception as e:
        print(f"Documents list failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting Employer System Tests...")
    print("=" * 50)
    
    # Test documents list (public endpoint)
    test_documents_list()
    
    # Test signup
    signup_success = test_employer_signup()
    
    # Test login
    if signup_success:
        token = test_employer_login()
        
        # Test document verification
        if token:
            test_document_verification(token)
        else:
            print("Skipping verification test - login failed")
    else:
        print("Skipping login test - signup failed")
    
    print("\n" + "=" * 50)
    print("Tests completed!")

if __name__ == "__main__":
    main()