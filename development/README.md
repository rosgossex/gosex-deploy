# Development Tools

## Random User Generator

Script to create random users in Keycloak "gosex" realm for development/testing purposes.

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

All generated users will have password: `password123`