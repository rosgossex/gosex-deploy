# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a deployment repository for GoSex services using Docker Compose orchestration. It manages the deployment of backend and authentication services as Git submodules.

## Architecture

The deployment uses Docker Compose with service includes to orchestrate:
- Backend service with PostgreSQL database
- ESIA authentication service with Keycloak and separate PostgreSQL

Services are defined in their respective submodule directories and included via:
```yaml
include:
  - ./gosex-backend/docker-compose.yml
  - ./gosex-esia/docker-compose.yml
```

## Common Development Tasks

### Initial Setup

```bash
# Clone with submodules
git clone https://github.com/rosgossex/gosex-deploy.git
git submodule update --init --recursive --remote

# Update submodules to latest
git submodule update --remote
```

### Deployment

```bash
# Deploy all services (requires .env file)
docker compose --env-file .env up -d --wait --build

# Deploy with specific env file
docker compose --env-file .env.dev up -d --wait --build

# Stop all services  
docker compose down

# View service logs
docker compose logs -f [service-name]
```

### Environment Configuration

Services require environment variables defined in `.env` file covering:
- Database configurations for both PostgreSQL instances
- Service authentication and networking settings  
- Container image versions and registry settings
- Port mappings and volume configurations

## Service Ports

- Backend application: 6969
- ESIA Keycloak admin: 8080  
- PostgreSQL (backend): 5432

## Git Workflow Rules

### Staging Files
- **NEVER use `git add .`** - Always explicitly specify file paths to stage
- Use specific paths: `git add path/to/file.ext` or `git add directory/`
- This prevents accidentally staging unintended files (secrets, temporary files, etc.)