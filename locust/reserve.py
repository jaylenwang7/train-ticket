import random
from datetime import datetime, timedelta
from typing import Dict, List
import json
from locust import FastHttpUser, LoadTestShape, task, tag, between, events
import time
import os
from pathlib import Path
import logging
import locust.stats

class UserCredentials:
    def __init__(self, username: str, password: str, user_id: str, token: str, contact_ids: List[str]):
        self.username = username
        self.password = password
        self.user_id = user_id
        self.token = token
        self.contact_ids = contact_ids

def load_credentials(filename: str = "user_credentials.json", debug: bool = True) -> List[UserCredentials]:
    """
    Load user credentials from a JSON file and convert them to UserCredentials objects.
    
    Args:
        filename (str): Path to the credentials JSON file
        debug (bool): If True, print debug information
        
    Returns:
        List[UserCredentials]: List of UserCredentials objects
    """
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
            
        if debug:
            print(f"Loaded {len(users)} users from {filename}")
        return users
        
    except FileNotFoundError:
        if debug:
            print(f"Error: Credentials file '{filename}' not found. "
                  f"Please run setup_users.py first.")
        return []
    except json.JSONDecodeError:
        if debug:
            print(f"Error: Invalid JSON in credentials file '{filename}'")
        return []
    except KeyError as e:
        if debug:
            print(f"Error: Missing required field in credentials file: {e}")
        return []

def load_stats_config():
    """
    Load Locust stats configuration from a JSON file if it exists,
    otherwise use default values.
    """
    # Default values
    default_config = {
        "CONSOLE_STATS_INTERVAL_SEC": 1,
        "HISTORY_STATS_INTERVAL_SEC": 60,
        "CSV_STATS_INTERVAL_SEC": 60,
        "CSV_STATS_FLUSH_INTERVAL_SEC": 60,
        "CURRENT_RESPONSE_TIME_PERCENTILE_WINDOW": 60,
        "PERCENTILES_TO_REPORT": [0.50, 0.75, 0.90, 0.99, 0.999, 0.9999, 0.99999, 1.0],
        "REQUEST_RATE_PER_USER": 1.0,
        "SPAWN_RATE": 100,
        "RANDOM_SEED": None
    }

    # Try to load config from JSON file
    config_path = os.path.join(os.path.dirname(__file__), 'locust_stats_config.json')
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
                default_config.update(loaded_config)
                print(f"Loaded configuration from {config_path}")
        else:
            print("No configuration file found, using defaults")
    except Exception as e:
        print(f"Error loading configuration: {e}")
        print("Using default values")

    # Apply configuration to locust.stats
    for key in ["CONSOLE_STATS_INTERVAL_SEC", "HISTORY_STATS_INTERVAL_SEC", 
               "CSV_STATS_INTERVAL_SEC", "CSV_STATS_FLUSH_INTERVAL_SEC",
               "CURRENT_RESPONSE_TIME_PERCENTILE_WINDOW", "PERCENTILES_TO_REPORT"]:
        setattr(locust.stats, key, default_config[key])

    return default_config

def print_config(config):
    """Print the current configuration settings"""
    print("\n=== Locust Configuration ===")
    for key, value in config.items():
        print(f"{key}: {value}")
    print("===========================\n")

# Load config and get request rate
app_config = load_stats_config()
print_config(app_config)
request_rate = app_config["REQUEST_RATE_PER_USER"]
spawn_rate = app_config["SPAWN_RATE"]
wait_time_seconds = 1.0 / request_rate

# Initialize random seed
seed = app_config["RANDOM_SEED"]
if seed is None:
    seed = time.time()
random.seed(seed)

# Define route configurations for each trip ID
# Format: trip_id: (route_id, [station1, station2, ...])
ROUTE_CONFIGS = {
    "G1234": ("92708982-77af-4318-be25-57ccb0ff69ad", ["nanjing", "zhenjiang", "wuxi", "suzhou", "shanghai"]),
    "G1235": ("aefcef3f-3f42-46e8-afd7-6cb2a928bd3d", ["nanjing", "shanghai"]),
    "G1236": ("a3f256c1-0e43-4f7d-9c21-121bf258101f", ["nanjing", "suzhou", "shanghai"]),
    "G1237": ("084837bb-53c8-4438-87c8-0321a4d09917", ["suzhou", "shanghai"]),
    "D1345": ("f3d4d4ef-693b-4456-8eed-59c0d717dd08", ["shanghai", "suzhou"])
}

def constant_pacing(wait_time):
    """
    Returns a function that ensures tasks run at a constant rate regardless of task execution time.
    """
    def wait_time_func(self):
        if not hasattr(self, "_cp_last_wait_time"):
            self._cp_last_wait_time = 0
            self._cp_last_run = time.time()
        run_time = time.time() - self._cp_last_run - self._cp_last_wait_time
        self._cp_last_wait_time = max(0, wait_time - run_time)
        self._cp_last_run = time.time()
        return self._cp_last_wait_time
    return wait_time_func

class ReservationUser(FastHttpUser):
    wait_time = constant_pacing(wait_time_seconds)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.users = load_credentials()
        
    def random_trip_id(self) -> str:
        """Return a random trip ID from the available options"""
        trip_ids = ["G1234", "G1235", "G1236", "G1237", "D1345"]
        return random.choice(trip_ids)

    def random_date(self) -> str:
        """Generate a random date between 2025-01-01 and 2035-12-31 with more spread"""
        # Extended date range to 10 years
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2035, 12, 31)
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_date + timedelta(days=random_number_of_days)
        return random_date.strftime("%Y-%m-%d")
    
    def get_valid_stations(self, trip_id: str) -> tuple:
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

    @task
    @tag('reserve_ticket')
    def reserve_ticket(self):
        if not self.users:
            return
            
        # Select a random user
        user = random.choice(self.users)
        contact_id = random.choice(user.contact_ids)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {user.token}"
        }
        
        # Use random trip ID instead of fixed one
        trip_id = self.random_trip_id()
        
        # Get valid start and end stations based on the trip ID
        from_station, to_station = self.get_valid_stations(trip_id)
        
        data = {
            "accountId": user.user_id,
            "contactsId": contact_id,
            "tripId": trip_id,
            "seatType": "3",
            "date": self.random_date(),
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
        
        with self.client.post(
            "/api/v1/preserveservice/preserve",
            json=data,
            headers=headers,
            catch_response=True,
            name='reserve_ticket'
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status code: {response.status_code}")

# Read RPS values from the 'rps.txt' file
RPS = list(map(int, Path('rps.txt').read_text().splitlines()))

class CustomShape(LoadTestShape):
    time_limit = len(RPS)
    spawn_rate = spawn_rate

    def tick(self):
        run_time = int(self.get_run_time())
        if run_time < self.time_limit:
            user_count = RPS[run_time]
            return (user_count, self.spawn_rate)
        return None