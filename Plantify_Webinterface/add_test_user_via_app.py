#!/usr/bin/env python3
"""
Alternative script to create a test user via the Flask app's registration endpoint.
This test user is clearly marked as a test account.
"""

import requests
import sys

# Flask app configuration
FLASK_APP_URL = 'http://localhost:8080'

# Test user configuration - CLEARLY MARKED AS TEST USER
TEST_USER_EMAIL = "test.user@plantify.test"
TEST_USER_PASSWORD = "TestUser123!"

def create_test_user_via_registration():
    """Create a test user using the Flask app's registration endpoint"""
    print(f"🧪 Creating test user via Flask registration: {TEST_USER_EMAIL}")
    print(f"📧 Email: {TEST_USER_EMAIL}")
    print(f"🔑 Password: {TEST_USER_PASSWORD}")
    print(f"⚠️  This is a TEST USER - clearly marked for testing purposes!")
    print("-" * 60)
    
    # Prepare registration data
    registration_data = {
        'email': TEST_USER_EMAIL,
        'password': TEST_USER_PASSWORD,
        'confirm_password': TEST_USER_PASSWORD
    }
    
    try:
        # Create a session to handle cookies
        session = requests.Session()
        
        # First, get the registration page to establish a session
        response = session.get(f"{FLASK_APP_URL}/register", timeout=10)
        if response.status_code != 200:
            print(f"❌ Could not access registration page. Status: {response.status_code}")
            return False
        
        # Submit the registration form
        response = session.post(
            f"{FLASK_APP_URL}/register",
            data=registration_data,
            timeout=10,
            allow_redirects=False  # Don't follow redirects to see the actual response
        )
        
        # Check if registration was successful
        if response.status_code == 302:  # Redirect indicates success
            print("✅ Test user created successfully via Flask registration!")
            print(f"📧 Email: {TEST_USER_EMAIL}")
            print(f"🔑 Password: {TEST_USER_PASSWORD}")
            print("⚠️  Remember: This is a TEST USER account!")
            return True
        elif response.status_code == 200:
            # Check if there's an error message in the response
            if "bereits registriert" in response.text or "already registered" in response.text:
                print("⚠️  Test user already exists!")
                print(f"📧 Email: {TEST_USER_EMAIL}")
                print(f"🔑 Password: {TEST_USER_PASSWORD}")
                return True
            else:
                print(f"❌ Registration failed. Response content indicates error.")
                print("Check if the Flask app is running and accessible.")
                return False
        else:
            print(f"❌ Failed to create test user. Status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Make sure it's running on http://localhost:8080")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Flask app might be slow or unresponsive.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function"""
    print("🧪 PLANTIFY TEST USER CREATOR (via Flask Registration)")
    print("=" * 55)
    
    # Create the test user
    success = create_test_user_via_registration()
    
    if success:
        print("\n🎉 Test user setup complete!")
        print("You can now use these credentials to test the application:")
        print(f"📧 Email: {TEST_USER_EMAIL}")
        print(f"🔑 Password: {TEST_USER_PASSWORD}")
        print(f"🌐 Login at: {FLASK_APP_URL}/login")
        print("\n⚠️  IMPORTANT: This is a TEST USER account!")
        print("🗑️  Delete this user when testing is complete.")
    else:
        print("\n❌ Failed to create test user.")
        print("Make sure the Flask app is running and accessible.")
        sys.exit(1)

if __name__ == "__main__":
    main()