# Development Tools

## Random User Generator

Script to create random users in Keycloak "gosex" realm and automatically register them in the backend for complete end-to-end testing.

### Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Usage

```bash
# Activate virtual environment first
source venv/bin/activate

# Create 10 random users (default)
python create_random_users.py

# Create specific number of users
python create_random_users.py 25
```

### Environment Variables

- `KEYCLOAK_ADMIN` - Admin username (default: "admin")
- `KEYCLOAK_ADMIN_PASSWORD` - Admin password (default: "admin")

### Prerequisites

- Keycloak must be running on localhost:8080
- "gosex" realm must exist
- Admin credentials must be valid

### Workflow

For each user, the script:
1. **Creates user in Keycloak** with random profile data
2. **Retrieves JWT token** using gosex-app client  
3. **Registers user in backend** via `/users/me` endpoint
4. **Reports results** for both Keycloak and backend registration

All generated users will have password: `password123`

### Output

The script shows detailed progress for each user:
- ✅ Keycloak user creation
- Token retrieval status  
- ✅ Backend registration with user ID
- Summary statistics

## User Login Script

Script to authenticate as a specific user and retrieve JWT tokens.

### Usage

```bash
# Activate virtual environment first
source venv/bin/activate

# Login as user and get JWT token
python login_user.py <username> <password> [client_id]

# Example with generated user
python login_user.py kuzminigor522 password123

# Example with custom client
python login_user.py username password my-client-id
```

### Output

The script displays:
- Authentication success/failure
- Token expiration time
- Decoded token payload information  
- Full JWT access token
- Refresh token (if available)
- **Backend registration result** - automatically registers/finds user in backend

### Backend Integration

The script automatically calls the backend `/users/me` endpoint with the JWT token:
- **201 Created**: User was created in backend (first time login)
- **200 OK**: User already exists in backend (returning user)  
- **Error**: Shows authentication or connection issues

This provides a complete login flow from Keycloak authentication to backend user registration.

Default client ID is `gosex-app` which includes user profile information in JWT tokens.

**Important:** The `admin-cli` client does NOT include user claims - use `gosex-app` for full functionality.