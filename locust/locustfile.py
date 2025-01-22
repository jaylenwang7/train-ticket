import random
from datetime import datetime, timedelta
from typing import Dict, List
import json
from locust import HttpUser, task, between
import json

class UserCredentials:
    def __init__(self, username: str, password: str, user_id: str, token: str, contact_ids: List[str]):
        self.username = username
        self.password = password
        self.user_id = user_id
        self.token = token
        self.contact_ids = contact_ids

def load_credentials(filename: str = "user_credentials.txt") -> List[UserCredentials]:
    users = []
    with open(filename, "r") as f:
        current_user = {}
        contact_ids = []
        
        for line in f:
            line = line.strip()
            if line.startswith("Username:"):
                current_user["username"] = line.split(":", 1)[1].strip()
            elif line.startswith("Password:"):
                current_user["password"] = line.split(":", 1)[1].strip()
            elif line.startswith("UserId:"):
                current_user["user_id"] = line.split(":", 1)[1].strip()
            elif line.startswith("Token:"):
                current_user["token"] = line.split(":", 1)[1].strip()
            elif line.startswith("Contact IDs:"):
                contact_ids = []
            elif line.startswith("  "):  # Contact ID entry
                contact_ids.append(line.strip())
            elif line == "":  # Empty line indicates end of user entry
                if current_user and contact_ids:
                    users.append(UserCredentials(
                        username=current_user["username"],
                        password=current_user["password"],
                        user_id=current_user["user_id"],
                        token=current_user["token"],
                        contact_ids=contact_ids
                    ))
                    current_user = {}
                    contact_ids = []
    
    return users

def constant_pacing(wait_time):
    """
    Returns a function that ensures tasks run at a constant rate regardless of task execution time.
    
    Args:
        wait_time: The desired time between task executions in seconds
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

class ReservationUser(HttpUser):
    wait_time = constant_pacing(1.0)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.users = load_credentials()
        
    def random_date(self) -> str:
        """Generate a random date between 2025-01-01 and 2030-12-31"""
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2030, 12, 31)
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_date + timedelta(days=random_number_of_days)
        return random_date.strftime("%Y-%m-%d")

    @task
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
        
        data = {
            "accountId": user.user_id,
            "contactsId": contact_id,
            "tripId": "D1345",
            "seatType": "3",
            "date": self.random_date(),
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
        
        with self.client.post(
            "/api/v1/preserveservice/preserve",
            json=data,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status code: {response.status_code}")