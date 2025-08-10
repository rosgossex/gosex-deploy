#!/usr/bin/env python3

import requests
import json
import sys
import os
from urllib.parse import urljoin

KEYCLOAK_URL = "http://localhost:8080"
BACKEND_URL = "http://localhost:6969"
REALM = "gosex"
CLIENT_ID = "gosex-app"

def get_user_token(username, password, client_id=None):
    """Get user access token from Keycloak"""
    if client_id is None:
        client_id = CLIENT_ID
    
    token_url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"
    
    data = {
        "client_id": client_id,
        "username": username,
        "password": password,
        "grant_type": "password"
    }
    
    try:
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            token_data = response.json()
            return token_data
        else:
            print(f"Error getting token: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Keycloak: {e}")
        return None

def decode_jwt_payload(token):
    """Decode JWT payload (basic decoding without verification)"""
    import base64
    try:
        # Split token and get payload
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        payload = parts[1]
        # Add padding if needed
        missing_padding = len(payload) % 4
        if missing_padding:
            payload += '=' * (4 - missing_padding)
        
        # Decode base64
        decoded = base64.b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        print(f"Error decoding JWT: {e}")
        return None

def register_user_with_backend(access_token):
    """Register/get user from backend using JWT token"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/users/me", headers=headers)
        return response.status_code, response.text
    except requests.exceptions.RequestException as e:
        return None, f"Error connecting to backend: {e}"

def main():
    if len(sys.argv) < 3:
        print("Usage: python login_user.py <username> <password> [client_id]")
        print("Example: python login_user.py kuzminigor522 password123")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    client_id = sys.argv[3] if len(sys.argv) > 3 else CLIENT_ID
    
    print(f"Logging in user '{username}' to realm '{REALM}'...")
    
    # Get token
    token_data = get_user_token(username, password, client_id)
    if not token_data:
        print("Failed to get token")
        sys.exit(1)
    
    access_token = token_data.get('access_token')
    refresh_token = token_data.get('refresh_token')
    expires_in = token_data.get('expires_in')
    
    print(f"\n✅ Successfully logged in!")
    print(f"Token expires in: {expires_in} seconds")
    
    # Decode and display token payload
    payload = decode_jwt_payload(access_token)
    if payload:
        print(f"\nToken payload:")
        print(f"  Subject (user ID): {payload.get('sub', 'N/A')}")
        print(f"  Username: {payload.get('preferred_username', 'N/A')}")
        print(f"  Email: {payload.get('email', 'N/A')}")
        print(f"  Given name: {payload.get('given_name', 'N/A')}")
        print(f"  Family name: {payload.get('family_name', 'N/A')}")
        print(f"  Issued at: {payload.get('iat', 'N/A')}")
        print(f"  Expires: {payload.get('exp', 'N/A')}")
        print(f"  Client: {payload.get('azp', 'N/A')}")
        print(f"  Scope: {payload.get('scope', 'N/A')}")
        print(f"  Roles: {payload.get('realm_access', {}).get('roles', [])}")
        
        # Show all payload for debugging
        print(f"\nFull payload:")
        for key, value in payload.items():
            print(f"  {key}: {value}")
    
    print(f"\n🔑 Access Token:")
    print(access_token)
    
    if refresh_token:
        print(f"\n🔄 Refresh Token:")
        print(refresh_token)
    
    # Test backend registration
    print(f"\n🌐 Testing backend registration...")
    status_code, response_text = register_user_with_backend(access_token)
    
    if status_code is None:
        print(f"❌ Backend connection failed: {response_text}")
    elif status_code == 200:
        print(f"✅ User found in backend (200)")
        try:
            user_data = json.loads(response_text)
            print(f"   User ID: {user_data.get('id')}")
            print(f"   Full Name: {user_data.get('fullName')}")
            print(f"   Email: {user_data.get('email', 'N/A')}")
        except:
            print(f"   Response: {response_text}")
    elif status_code == 201:
        print(f"✅ User created in backend (201)")
        try:
            user_data = json.loads(response_text)
            print(f"   User ID: {user_data.get('id')}")
            print(f"   Full Name: {user_data.get('fullName')}")
            print(f"   Birthdate: {user_data.get('birthdate')}")
            print(f"   Gender: {user_data.get('gender')}")
        except:
            print(f"   Response: {response_text}")
    else:
        print(f"❌ Backend error ({status_code}): {response_text}")

if __name__ == "__main__":
    main()