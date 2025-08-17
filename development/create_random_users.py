#!/usr/bin/env python3

import requests
import json
import random
import string
from faker import Faker
import sys
import os
from urllib.parse import urljoin

fake = Faker('ru_RU')

KEYCLOAK_URL = "http://localhost:8080"
BACKEND_URL = "http://localhost:6969"
REALM = "gosex"
ADMIN_CLIENT_ID = "admin-cli"
USER_CLIENT_ID = "gosex-app"

def get_admin_token(username="admin", password="admin"):
    """Get admin access token from Keycloak"""
    token_url = f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token"
    
    data = {
        "client_id": ADMIN_CLIENT_ID,
        "username": username,
        "password": password,
        "grant_type": "password"
    }
    
    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.exceptions.RequestException as e:
        print(f"Error getting admin token: {e}")
        return None

def create_user(token, user_data):
    """Create a user in Keycloak"""
    users_url = f"{KEYCLOAK_URL}/admin/realms/{REALM}/users"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(users_url, headers=headers, json=user_data)
        if response.status_code == 201:
            return True
        else:
            print(f"Error creating user {user_data['username']}: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error creating user {user_data['username']}: {e}")
        return False

def get_user_token(username, password):
    """Get user access token from Keycloak"""
    token_url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"
    
    data = {
        "client_id": USER_CLIENT_ID,
        "username": username,
        "password": password,
        "grant_type": "password"
    }
    
    try:
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            return None
    except requests.exceptions.RequestException:
        return None

def register_user_with_backend(access_token, username):
    """Register/get user from backend using JWT token"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/users/me", headers=headers)
        return response.status_code, response.text
    except requests.exceptions.RequestException as e:
        return None, str(e)

def generate_random_user():
    """Generate random user data"""
    username = fake.user_name() + str(random.randint(100, 999))
    
    # Generate random birthdate (18-80 years old)
    birthdate = fake.date_of_birth(minimum_age=18, maximum_age=80).strftime("%Y-%m-%d")
    
    # Random gender
    gender = random.choice(["male", "female"])
    
    user_data = {
        "username": username,
        "enabled": True,
        "emailVerified": True,
        "firstName": fake.first_name(),
        "lastName": fake.last_name(),
        "email": f"{username}@example.com",
        "credentials": [{
            "type": "password",
            "value": "password123",
            "temporary": False
        }],
        "attributes": {
            "phone": [fake.phone_number()],
            "city": [fake.city()],
            "birthdate": [birthdate],
            "gender": [gender]
        }
    }
    
    return user_data

def main():
    print("Creating random users in Keycloak...")
    
    # Get admin credentials from environment or use defaults
    admin_user = os.getenv("KEYCLOAK_ADMIN", "admin")
    admin_pass = os.getenv("KEYCLOAK_ADMIN_PASSWORD", "admin")
    
    # Get admin token
    token = get_admin_token(admin_user, admin_pass)
    if not token:
        print("Failed to get admin token. Make sure Keycloak is running and credentials are correct.")
        sys.exit(1)
    
    # Number of users to create
    num_users = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    print(f"Creating {num_users} random users...")
    
    created_count = 0
    registered_count = 0
    
    for i in range(num_users):
        user_data = generate_random_user()
        username = user_data['username']
        password = user_data['credentials'][0]['value']
        
        # Create user in Keycloak
        if create_user(token, user_data):
            created_count += 1
            print(f"✅ Created user: {username} ({user_data['firstName']} {user_data['lastName']})")
            
            # Get user token and register with backend
            print(f"   Getting token for {username}...")
            user_token = get_user_token(username, password)
            
            if user_token:
                print(f"   Token obtained, registering with backend...")
                status_code, response_text = register_user_with_backend(user_token, username)
                
                if status_code == 201:
                    registered_count += 1
                    try:
                        user_data_backend = json.loads(response_text)
                        print(f"   ✅ Registered in backend: {user_data_backend.get('fullName')} (ID: {user_data_backend.get('id')})")
                    except:
                        print(f"   ✅ Registered in backend (201)")
                elif status_code == 200:
                    registered_count += 1
                    print(f"   ✅ Found existing user in backend (200)")
                else:
                    print(f"   ❌ Backend error ({status_code}): {response_text}")
            else:
                print(f"   ❌ Failed to get user token")
        else:
            print(f"❌ Failed to create user: {username}")
        
        print()  # Empty line between users
        
    print(f"Summary:")
    print(f"  Users created in Keycloak: {created_count}/{num_users}")
    print(f"  Users registered in backend: {registered_count}/{created_count}")

if __name__ == "__main__":
    main()