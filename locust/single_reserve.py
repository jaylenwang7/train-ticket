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
    end_date = datetime(2035, 12, 31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    return random_date.strftime("%Y-%m-%d")

def random_trip_id():
    """Return a random trip ID from the available options"""
    trip_ids = ["G1234", "G1235", "G1236", "G1237", "D1345"]
    return random.choice(trip_ids)

# Define route configurations for each trip ID
# Format: trip_id: (route_id, [station1, station2, ...])
ROUTE_CONFIGS = {
    "G1234": ("92708982-77af-4318-be25-57ccb0ff69ad", ["nanjing", "zhenjiang", "wuxi", "suzhou", "shanghai"]),
    "G1235": ("aefcef3f-3f42-46e8-afd7-6cb2a928bd3d", ["nanjing", "shanghai"]),
    "G1236": ("a3f256c1-0e43-4f7d-9c21-121bf258101f", ["nanjing", "suzhou", "shanghai"]),
    "G1237": ("084837bb-53c8-4438-87c8-0321a4d09917", ["suzhou", "shanghai"]),
    "D1345": ("f3d4d4ef-693b-4456-8eed-59c0d717dd08", ["shanghai", "suzhou"])
}

def get_valid_stations(trip_id):
    """
    Get valid start and end stations for a given trip ID based on the route configuration.
    
    Args:
        trip_id (str): The trip ID
        
    Returns:
        tuple: (start_station, end_station)
    """
    if trip_id not in ROUTE_CONFIGS:
        # Default to shanghai and suzhou if trip_id is not found
        return "shanghai", "suzhou"
        
    _, stations = ROUTE_CONFIGS[trip_id]
    
    # If there are only two stations, use them directly
    if len(stations) == 2:
        return stations[0], stations[1]
        
    # For routes with more than two stations, randomly select a start station
    # and ensure the end station comes after it in the route
    start_idx = random.randint(0, len(stations) - 2)
    end_idx = random.randint(start_idx + 1, len(stations) - 1)
    
    return stations[start_idx], stations[end_idx]

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
    
    # Use random trip ID instead of fixed one
    trip_id = random_trip_id()
    
    # Get valid start and end stations based on the trip ID
    from_station, to_station = get_valid_stations(trip_id)
    
    data = {
        "accountId": user.user_id,
        "contactsId": contact_id,
        "tripId": trip_id,
        "seatType": "3",
        "date": random_date(),
        "from": from_station,
        "to": to_station,
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