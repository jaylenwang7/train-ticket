import requests
import json

# Base URL
BASE_URL = "http://localhost:30080"

# Function to create a new user
def create_user(username, password, user_id):
    url = f"{BASE_URL}/api/v1/auth"
    
    payload = {
        "userName": username,
        "password": password,
        "userId": user_id
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during user creation: {e}")
        return None

# Function to login
def login_user(username, password):
    url = f"{BASE_URL}/api/v1/users/login"
    
    payload = {
        "username": username,
        "password": password,
        "verificationCode": "1234"  # Assuming a static verification code, adjust if needed
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during login: {e}")
        return None

# Main execution
if __name__ == "__main__":
    # User details
    username = "newuser123"
    password = "securepassword456"
    user_id = "user789"
    
    # Create user
    create_result = create_user(username, password, user_id)
    
    if create_result:
        print("User created successfully:")
        print(json.dumps(create_result, indent=2))
        
        # Login with the newly created user
        login_result = login_user(username, password)
        
        if login_result:
            print("\nLogin successful:")
            print(json.dumps(login_result, indent=2))
            
            # Check if a token is returned and print it
            if 'data' in login_result and 'token' in login_result['data']:
                print(f"\nAuth Token: {login_result['data']['token']}")
            else:
                print("\nNo auth token found in the response.")
        else:
            print("\nLogin failed.")
    else:
        print("Failed to create user.")