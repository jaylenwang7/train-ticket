#!/usr/bin/env python3
import argparse
import json
import random
import requests
from datetime import datetime
import sys

class UserSetup:
    def __init__(self, base_url="http://localhost:30080"):
        self.base_url = base_url
        self.credentials_file = "user_credentials.txt"
        
    def create_user(self):
        """Simulate user creation - replace with actual API calls"""
        # This is a placeholder - implement actual API calls based on your service
        user = {
            "username": f"user_{random.randint(1000, 9999)}",
            "password": f"pass_{random.randint(1000, 9999)}",
            "id": str(random.randint(10000, 99999)),
            "token": f"token_{random.randint(100000, 999999)}",
            "contact_ids": [str(random.randint(1000, 9999)) for _ in range(3)]
        }
        return user
    
    def save_credentials(self, user):
        """Save user credentials to file"""
        with open(self.credentials_file, "a") as f:
            f.write(f"Username: {user['username']}\n")
            f.write(f"Password: {user['password']}\n")
            f.write(f"UserId: {user['id']}\n")
            f.write(f"Token: {user['token']}\n")
            f.write("Contact IDs:\n")
            for contact_id in user['contact_ids']:
                f.write(f"    {contact_id}\n")
            f.write("\n")

    def setup_users(self, num_users):
        """Create specified number of users"""
        print(f"Creating {num_users} users...")
        
        # Clear the file first
        open(self.credentials_file, "w").close()
        
        for i in range(num_users):
            user = self.create_user()
            self.save_credentials(user)
            if (i + 1) % 100 == 0:
                print(f"Created {i + 1} users")
        
        print(f"Finished creating {num_users} users")

def main():
    parser = argparse.ArgumentParser(description='Setup users for load testing')
    parser.add_argument('-n', '--num-users', type=int, default=1000,
                      help='Number of users to create (default: 1000)')
    parser.add_argument('--base-url', type=str, default="http://localhost:30080",
                      help='Base URL of the service (default: http://localhost:30080)')
    
    args = parser.parse_args()
    
    setup = UserSetup(base_url=args.base_url)
    setup.setup_users(args.num_users)

if __name__ == "__main__":
    main()