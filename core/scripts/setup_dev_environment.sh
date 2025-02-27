#!/bin/bash
# Setup Development Environment Script for PillChecker
# This script initializes everything needed for local development

set -e

# Text colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}   Setting up PillChecker Development Environment   ${NC}"
echo -e "${BLUE}=============================================${NC}"

# Check if Docker is running
echo -e "\n${YELLOW}Checking if Docker is running...${NC}"
if ! docker info > /dev/null 2>&1; then
  echo -e "${RED}Docker is not running or not installed.${NC}"
  echo -e "Please start Docker and try again."
  exit 1
fi
echo -e "${GREEN}Docker is running!${NC}"

# Check if Python is installed
echo -e "\n${YELLOW}Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
  echo -e "${RED}Python 3 is not installed.${NC}"
  echo -e "Please install Python 3.9+ and try again."
  exit 1
fi
python3 --version
echo -e "${GREEN}Python is installed!${NC}"

# Create Python virtual environment
echo -e "\n${YELLOW}Setting up Python virtual environment...${NC}"
if [ ! -d ".venv" ]; then
  echo "Creating new virtual environment..."
  python3 -m venv .venv
else
  echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo -e "\n${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}Dependencies installed!${NC}"

# Create Supabase volume directories
echo -e "\n${YELLOW}Creating Supabase volume directories...${NC}"
mkdir -p supabase/volumes/api
mkdir -p supabase/volumes/storage
echo -e "${GREEN}Directories created!${NC}"

# Create environment files
echo -e "\n${YELLOW}Creating environment files...${NC}"

# Main .env file
cat > .env << EOL
# Common environment variables for all services

# JWT and security
JWT_SECRET=super-secret-jwt-token-with-at-least-32-characters-long

# Database connection
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
POSTGRES_PORT=5432
POSTGRES_HOST=supabase-db

# Supabase tokens
ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.OXIIWX5RmrYetGRNFVJ0QnX0vaXdVmUhxnaBP1WDs0I
SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU

# Service URLs
KONG_URL=http://kong:8000
SUPABASE_URL=http://kong:8000
META_URL=http://meta:8080
AUTH_URL=http://supabase-auth:9999
REST_URL=http://supabase-rest:3000
STORAGE_URL=http://supabase-storage:5000
MAILHOG_URL=http://mailhog:1025

# Storage configuration
STORAGE_BUCKET=scans
EOL

# Supabase DB environment
cat > .env.supabase-db << EOL
# Environment variables for the Supabase PostgreSQL database

# These values are already defined in the common .env file, 
# but they're included here for clarity
POSTGRES_USER=\${POSTGRES_USER}
POSTGRES_PASSWORD=\${POSTGRES_PASSWORD}
POSTGRES_DB=\${POSTGRES_DB}
EOL

# Supabase Studio environment
cat > .env.supabase-studio << EOL
# Environment variables for the Supabase Studio

SUPABASE_URL=\${KONG_URL}
STUDIO_PG_META_URL=\${META_URL}
SUPABASE_SERVICE_KEY=\${SERVICE_KEY}
PG_META_PORT=8080
EOL

# Kong environment
cat > .env.kong << EOL
# Environment variables for Kong API Gateway

KONG_DATABASE=off
KONG_DECLARATIVE_CONFIG=/var/lib/kong/kong.yml
KONG_DNS_ORDER=LAST,A,CNAME
KONG_PLUGINS=request-transformer,cors,key-auth,acl
EOL

# Supabase Auth environment
cat > .env.supabase-auth << EOL
# Environment variables for Supabase Auth (GoTrue)

GOTRUE_API_HOST=0.0.0.0
GOTRUE_API_PORT=9999
GOTRUE_JWT_SECRET=\${JWT_SECRET}
GOTRUE_JWT_EXP=3600
GOTRUE_JWT_DEFAULT_GROUP_NAME=authenticated

# Database configuration
GOTRUE_DB_DRIVER=postgres
GOTRUE_DB_HOST=\${POSTGRES_HOST}
GOTRUE_DB_PORT=\${POSTGRES_PORT}
GOTRUE_DB_USER=\${POSTGRES_USER}
GOTRUE_DB_PASSWORD=\${POSTGRES_PASSWORD}
GOTRUE_DB_DATABASE=\${POSTGRES_DB}

# Email configuration
GOTRUE_SITE_URL=http://localhost:3000
GOTRUE_SMTP_HOST=mailhog
GOTRUE_SMTP_PORT=1025
GOTRUE_SMTP_ADMIN_EMAIL=admin@example.com
GOTRUE_MAILER_AUTOCONFIRM=true
GOTRUE_SMTP_SENDER_NAME=PillChecker
EOL

# Supabase REST environment
cat > .env.supabase-rest << EOL
# Environment variables for Supabase REST API (PostgREST)

PGRST_DB_URI=postgres://\${POSTGRES_USER}:\${POSTGRES_PASSWORD}@\${POSTGRES_HOST}:\${POSTGRES_PORT}/\${POSTGRES_DB}
PGRST_DB_SCHEMA=public,storage
PGRST_DB_ANON_ROLE=anon
PGRST_JWT_SECRET=\${JWT_SECRET}
EOL

# Supabase Storage environment
cat > .env.supabase-storage << EOL
# Environment variables for Supabase Storage API

ANON_KEY=\${ANON_KEY}
SERVICE_KEY=\${SERVICE_KEY}
POSTGREST_URL=\${REST_URL}
PGRST_JWT_SECRET=\${JWT_SECRET}
DATABASE_URL=postgres://\${POSTGRES_USER}:\${POSTGRES_PASSWORD}@\${POSTGRES_HOST}:\${POSTGRES_PORT}/\${POSTGRES_DB}
TENANT_ID=stub
REGION=stub
GLOBAL_S3_BUCKET=stub
ENABLE_IMAGE_TRANSFORMATION=true
FILE_SIZE_LIMIT=52428800
STORAGE_BACKEND=file
FILE_STORAGE_BACKEND_PATH=/var/lib/storage
PGOPTIONS="-c search_path=storage"
EOL

# Meta environment
cat > .env.meta << EOL
# Environment variables for Supabase Meta Service

PG_META_PORT=8080
PG_META_DB_HOST=\${POSTGRES_HOST}
PG_META_DB_PORT=\${POSTGRES_PORT}
PG_META_DB_NAME=\${POSTGRES_DB}
PG_META_DB_USER=\${POSTGRES_USER}
PG_META_DB_PASSWORD=\${POSTGRES_PASSWORD}
EOL

# App environment
cat > .env.app << EOL
# Environment variables for the PillChecker application

# Application environment
APP_ENV=development
DEBUG=True
SECRET_KEY=local-dev-secret-key

# API settings
API_V1_STR=/api/v1
PROJECT_NAME=PillChecker

# Supabase settings - point to local services
SUPABASE_URL=\${SUPABASE_URL}
SUPABASE_KEY=\${ANON_KEY}
SUPABASE_JWT_SECRET=\${JWT_SECRET}
SUPABASE_STORAGE_BUCKET=\${STORAGE_BUCKET}

# Database settings - use local Supabase DB
DEV_DATABASE_USER=\${POSTGRES_USER}
DEV_DATABASE_PASSWORD=\${POSTGRES_PASSWORD}
DEV_DATABASE_HOST=\${POSTGRES_HOST}
DEV_DATABASE_PORT=\${POSTGRES_PORT}
DEV_DATABASE_NAME=\${POSTGRES_DB}
EOL

echo -e "${GREEN}Environment files created!${NC}"

# Create Kong configuration
echo -e "\n${YELLOW}Creating Kong configuration...${NC}"
cat > supabase/volumes/api/kong.yml << EOL
_format_version: "2.1"
services:
  - name: auth-v1
    url: http://supabase-auth:9999
    routes:
      - name: auth-v1
        paths:
          - /auth/*
    plugins:
      - name: cors
  - name: rest-v1
    url: http://supabase-rest:3000
    routes:
      - name: rest-v1-all
        paths:
          - /rest/*
    plugins:
      - name: cors
  - name: storage-v1
    url: http://supabase-storage:5000
    routes:
      - name: storage-v1-all
        paths:
          - /storage/*
    plugins:
      - name: cors
EOL
echo -e "${GREEN}Kong configuration created!${NC}"

# Start Docker Compose
echo -e "\n${YELLOW}Starting Docker Compose services...${NC}"
docker-compose down -v > /dev/null 2>&1 || true  # Stop and remove previous containers, ignore errors
docker-compose up -d
echo -e "${GREEN}Docker services started!${NC}"

# Wait for services to be ready
echo -e "\n${YELLOW}Waiting for services to be ready...${NC}"
echo "This may take a minute or two..."
sleep 10  # Initial sleep to give services time to start

# Check if database is ready
MAX_RETRIES=30
RETRY=0

echo "Checking database connection..."
while ! docker-compose exec -T supabase-db pg_isready -U postgres > /dev/null 2>&1; do
  RETRY=$((RETRY+1))
  if [ $RETRY -eq $MAX_RETRIES ]; then
    echo -e "${RED}Database not ready after $MAX_RETRIES attempts. Exiting.${NC}"
    exit 1
  fi
  echo "Waiting for database to be ready... ($RETRY/$MAX_RETRIES)"
  sleep 2
done
echo -e "${GREEN}Database is ready!${NC}"

# Run database migrations
echo -e "\n${YELLOW}Applying database migrations...${NC}"
docker-compose exec -T app python scripts/db_management.py apply_migrations
echo -e "${GREEN}Migrations applied!${NC}"

# Print access URLs
echo -e "\n${BLUE}=============================================${NC}"
echo -e "${GREEN}Setup complete! You can access the services at:${NC}"
echo -e "- PillChecker App: ${BLUE}http://localhost:8000${NC}"
echo -e "- Supabase Studio: ${BLUE}http://localhost:54323${NC}"
echo -e "- MailHog (Email Testing): ${BLUE}http://localhost:8025${NC}"
echo -e "${BLUE}=============================================${NC}"

echo -e "\n${GREEN}Happy coding!${NC}" 