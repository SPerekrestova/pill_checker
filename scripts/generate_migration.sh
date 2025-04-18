#!/bin/bash

# Script to generate a new database migration

# Define colors for pretty output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}PillChecker Migration Generator${NC}"
echo -e "${YELLOW}==============================${NC}\n"

# Check if a migration name was provided
if [ -z "$1" ]; then
  echo -e "${RED}Error: Migration name is required.${NC}"
  echo "Usage: ./scripts/generate_migration.sh <migration_name>"
  exit 1
fi

MIGRATION_NAME=$1

# Step 1: Generate Alembic migration
echo -e "${GREEN}Generating Alembic migration '${MIGRATION_NAME}'...${NC}"
if ! alembic revision --autogenerate -m "$MIGRATION_NAME"; then
    echo -e "${RED}Failed to generate Alembic migration.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Alembic migration generated successfully.${NC}\n"

# Step 2: Generate Supabase migration
echo -e "${GREEN}Generating Supabase migration...${NC}"
echo -e "${YELLOW}Note: Supabase migrations require the database to be stopped.${NC}"

read -p "Do you want to stop Supabase to generate a migration file? (y/n): " choice
if [[ "$choice" =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}Stopping Supabase services...${NC}"
    supabase stop

    echo -e "${GREEN}Generating Supabase migration '${MIGRATION_NAME}'...${NC}"
    supabase db diff -f "$MIGRATION_NAME"

    echo -e "${GREEN}Starting Supabase services again...${NC}"
    supabase start

    echo -e "${GREEN}✓ Supabase migration generated successfully.${NC}"
else
    echo -e "${YELLOW}Skipped Supabase migration generation.${NC}"
    echo "You can manually generate it later with:"
    echo "  supabase stop"
    echo "  supabase db diff -f \"$MIGRATION_NAME\""
    echo "  supabase start"
fi

echo -e "\n${GREEN}Migration generation complete!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Review the generated migration files"
echo "2. Apply the migrations with: alembic upgrade head"
