#!/usr/bin/env python3
import random
import json
import requests
from datetime import datetime, timedelta
import argparse
import sys

class UserCredentials:
    def __init__(self, username, password, user_id, token, contact_ids):
        self.username = username
        self.password = password
        self.user_id = user_id
        self.token = token
        self.contact_ids = contact_ids

def load_credentials(filename="user_credentials.json"):
    """Load user credentials from a JSON file"""
    try:
        with open(filename, 'r') as f:
            users_data = json.load(f)
            
        users = []
        for user_data in users_data:
            user = UserCredentials(
                username=user_data['username'],
                password=user_data['password'],
                user_id=user_data['id'],
                token=user_data['token'],
                contact_ids=user_data['contact_ids']
            )
            users.append(user)
            
        print(f"Loaded {len(users)} users from {filename}")
        return users
        
    except FileNotFoundError:
        print(f"Error: Credentials file '{filename}' not found. "
              f"Please run setup_users.py first.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in credentials file '{filename}'")
        return []
    except KeyError as e:
        print(f"Error: Missing required field in credentials file: {e}")
        return []

def random_date():
    """Generate a random date between 2025-01-01 and 2030-12-31"""
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2030, 12, 31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    return random_date.strftime("%Y-%m-%d")

def make_reservation(base_url, user):
    """Make a single reservation request"""
    if not user.contact_ids:
        print("Error: User has no contact IDs")
        return False
        
    # Select a random contact ID
    contact_id = random.choice(user.contact_ids)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {user.token}"
    }
    
    data = {
        "accountId": user.user_id,
        "contactsId": contact_id,
        "tripId": "D1345",
        "seatType": "3",
        "date": random_date(),
        "from": "shanghai",
        "to": "suzhou",
        "assurance": "1",
        "foodType": 1,
        "foodName": "Rice",
        "foodPrice": 1.2,
        "stationName": "",
        "storeName": "",
        "handleDate": datetime.now().strftime("%Y-%m-%d"),
        "consigneeName": "ASDF",
        "consigneePhone": "123-456-7890",
        "consigneeWeight": 123,
        "isWithin": False
    }
    
    url = f"{base_url}/api/v1/preserveservice/preserve"
    
    # Print request details
    print("\n=== REQUEST DETAILS ===")
    print(f"URL: {url}")
    print("Headers:")
    for key, value in headers.items():
        # Mask the token for security
        if key == "Authorization":
            print(f"  {key}: Bearer [REDACTED]")
        else:
            print(f"  {key}: {value}")
    print("Data:")
    print(json.dumps(data, indent=2))
    print("=====================\n")
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("Reservation successful!")
            return True
        else:
            print(f"Reservation failed with status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error making reservation: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Make a single reservation request')
    parser.add_argument('--base-url', default='http://localhost:30080', 
                        help='Base URL of the API (default: http://localhost:30080)')
    parser.add_argument('--credentials', default='user_credentials.json',
                        help='Path to credentials file (default: user_credentials.json)')
    parser.add_argument('--username', help='Username to use (if not specified, a random user will be selected)')
    
    args = parser.parse_args()
    
    # Load users
    users = load_credentials(args.credentials)
    if not users:
        sys.exit(1)
    
    # Select user
    if args.username:
        user = next((u for u in users if u.username == args.username), None)
        if not user:
            print(f"User '{args.username}' not found in credentials file")
            sys.exit(1)
    else:
        user = random.choice(users)
    
    print(f"Using user: {user.username} (ID: {user.user_id})")
    
    # Make reservation
    success = make_reservation(args.base_url, user)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 