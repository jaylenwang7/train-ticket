#!/usr/bin/env python3
import argparse
import json
import random
import requests
from datetime import datetime
import sys
from tqdm import tqdm
import time

class UserSetup:
    def __init__(self, base_url="http://localhost:30080"):
        self.base_url = base_url
        self.credentials_file = "user_credentials.json"
        
    def random_string(self, length):
        return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=length))

    def make_request(self, method, url, body=None, auth_token=None):
        headers = {
            "Proxy-Connection": "keep-alive",
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Content-Type": "application/json",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive"
        }
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        response = requests.request(method, url, headers=headers, json=body)
        if response.status_code != 200:
            print(f"Request failed: {response.status_code} {response.text}")
        return response.json(), response.status_code

    def get_admin_token(self):
        print("Getting admin token...")
        login_response, login_code = self.make_request("POST", f"{self.base_url}/api/v1/users/login", {
            "username": "admin",
            "password": "222222",
            "verificationCode": "123"
        })

        if login_code != 200 or not login_response.get('data') or not login_response['data'].get('token'):
            print("Error logging in as admin.")
            return None

        print("Admin logged in successfully")
        return login_response['data']['token']

    def create_contact(self, admin_token, user_id, document_type):
        contact_data = {
            "accountId": user_id,
            "name": f"Contact_{document_type}",
            "documentType": document_type,
            "documentNumber": self.random_string(10),
            "phoneNumber": str(random.randint(1000000000, 9999999999))
        }
        
        create_response, create_code = self.make_request("POST", f"{self.base_url}/api/v1/adminbasicservice/adminbasic/contacts", contact_data, admin_token)

        if create_code != 200 or not create_response.get('data'):
            print("Error creating contact.")
            return None

        return create_response['data']

    def get_user_contact_ids(self, admin_token, user_id):
        contacts_response, contacts_code = self.make_request("GET", f"{self.base_url}/api/v1/adminbasicservice/adminbasic/contacts", None, admin_token)

        if contacts_code != 200 or not contacts_response.get('data'):
            print("Error fetching contacts.")
            return None

        user_contacts = [contact['id'] for contact in contacts_response['data'] if contact['accountId'] == user_id]
        return user_contacts

    def create_user(self, admin_token):
        username = self.random_string(8)
        password = self.random_string(10)

        create_response, create_code = self.make_request("POST", f"{self.base_url}/api/v1/adminuserservice/users", {
            "userName": username,
            "password": password,
            "gender": "0",
            "documentType": "1"
        }, admin_token)

        if create_code != 200:
            print("Error creating user.")
            return None, None

        return username, password

    def login_user(self, username, password):
        login_response, login_code = self.make_request("POST", f"{self.base_url}/api/v1/users/login", {
            "username": username,
            "password": password,
            "verificationCode": "123"
        })

        if login_code != 200 or login_response.get('status') != 1 or not login_response.get('data'):
            print("Error logging in with new user.")
            return None

        return login_response['data']

    def setup_users(self, num_users):
        print(f"Creating {num_users} users...")
        
        # Initialize an empty list to store all users
        all_users = []
        
        admin_token = self.get_admin_token()
        if not admin_token:
            print("Failed to get admin token. Exiting.")
            sys.exit(1)

        start_time = time.time()

        # Use tqdm to track progress
        for i in tqdm(range(num_users), desc="Creating users"):
            username, password = self.create_user(admin_token)
            if not username or not password:
                continue

            user_data = self.login_user(username, password)
            if not user_data:
                continue

            user_id = user_data['userId']
            contact1 = self.create_contact(admin_token, user_id, "1")
            contact2 = self.create_contact(admin_token, user_id, "2")

            if not contact1 or not contact2:
                continue

            user_contact_ids = self.get_user_contact_ids(admin_token, user_id)
            if not user_contact_ids:
                continue

            all_users.append({
                "username": username,
                "password": password,
                "id": user_id,
                "token": user_data['token'],
                "contact_ids": user_contact_ids
            })

        # Save all users at once
        with open(self.credentials_file, "w") as f:
            json.dump(all_users, f)

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Finished creating {num_users} users in {elapsed_time:.2f} seconds")

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