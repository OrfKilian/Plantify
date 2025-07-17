#!/usr/bin/env python3
"""
Script to create a test user for the Plantify application.
This test user is clearly marked as a test account.
"""

import os
import sys
import base64
import hashlib
import urllib.parse
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# API Configuration
API_BASE = 'http://plantify-api:5001'

# Test user configuration - CLEARLY MARKED AS TEST USER
TEST_USER_EMAIL = "test.user@plantify.test"
TEST_USER_PASSWORD = "TestUser123!"
TEST_USER_DISPLAY_NAME = "🧪 TEST USER - DO NOT DELETE"

def hash_password(password: str, iterations: int = 100_000) -> str:
    """Hash a password using PBKDF2 with salt - same as in app.py"""
    salt = os.urandom(16)
    hash_bytes = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    salt_b64 = base64.b64encode(salt).decode()
    hash_b64 = base64.b64encode(hash_bytes).decode()
    value = f"{iterations}${salt_b64}${hash_b64}"
    return urllib.parse.quote_plus(value)

def create_test_user():
    """Create a test user in the system"""
    print(f"🧪 Creating test user: {TEST_USER_EMAIL}")
    print(f"📧 Email: {TEST_USER_EMAIL}")
    print(f"🔑 Password: {TEST_USER_PASSWORD}")
    print(f"⚠️  This is a TEST USER - clearly marked for testing purposes!")
    print("-" * 60)
    
    # Hash the password
    hashed_password = hash_password(TEST_USER_PASSWORD)
    
    # Prepare the data for API request
    user_data = {
        "user_mail": TEST_USER_EMAIL,
        "password_hash": hashed_password
    }
    
    try:
        # Make API request to create user
        response = requests.post(
            f"{API_BASE}/insert/insert-user",
            json=user_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Test user created successfully!")
            print(f"📧 Email: {TEST_USER_EMAIL}")
            print(f"🔑 Password: {TEST_USER_PASSWORD}")
            print("⚠️  Remember: This is a TEST USER account!")
            return True
        else:
            print(f"❌ Failed to create test user. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the API server is running.")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out. API server might be slow or unresponsive.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function"""
    print("🧪 PLANTIFY TEST USER CREATOR")
    print("=" * 40)
    
    # Check if we can connect to the API
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code != 200:
            print("⚠️  API health check failed. Continuing anyway...")
    except:
        print("⚠️  Could not perform API health check. Continuing anyway...")
    
    # Create the test user
    success = create_test_user()
    
    if success:
        print("\n🎉 Test user setup complete!")
        print("You can now use these credentials to test the application:")
        print(f"📧 Email: {TEST_USER_EMAIL}")
        print(f"🔑 Password: {TEST_USER_PASSWORD}")
        print("\n⚠️  IMPORTANT: This is a TEST USER account!")
        print("🗑️  Delete this user when testing is complete.")
    else:
        print("\n❌ Failed to create test user.")
        sys.exit(1)

if __name__ == "__main__":
    main()