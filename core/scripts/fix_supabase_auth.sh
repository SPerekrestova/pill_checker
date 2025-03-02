#!/bin/bash
set -e

echo "🔧 Fixing Supabase Auth Migration Issues..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "❌ Docker is not running. Please start Docker and try again."
  exit 1
fi

# Check if containers are running
if ! docker ps | grep -q "core-supabase-db-1"; then
  echo "❌ Supabase containers are not running. Please start them with 'docker compose up -d' first."
  exit 1
fi

echo "✓ Found running Supabase containers"

# Stop auth service first
echo "📝 Stopping auth service..."
docker compose stop supabase-auth

# Create auth schema if it doesn't exist
echo "📝 Creating auth schema if it doesn't exist..."
docker exec core-supabase-db-1 psql -U postgres -c "CREATE SCHEMA IF NOT EXISTS auth;"

# Check for factor_type enum in auth schema
echo "📝 Checking for factor_type enum in auth schema..."
if ! docker exec core-supabase-db-1 psql -U postgres -c "SELECT 1 FROM pg_type t JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace WHERE t.typname = 'factor_type' AND n.nspname = 'auth';" | grep -q "1 row"; then
  echo "📝 Creating auth.factor_type enum..."
  docker exec core-supabase-db-1 psql -U postgres -c "CREATE TYPE auth.factor_type AS ENUM ('totp', 'webauthn', 'phone');"
  echo "✓ Created auth.factor_type enum"
else
  echo "✓ auth.factor_type enum already exists"
fi

# Check for factor_status enum in auth schema
echo "📝 Checking for factor_status enum in auth schema..."
if ! docker exec core-supabase-db-1 psql -U postgres -c "SELECT 1 FROM pg_type t JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace WHERE t.typname = 'factor_status' AND n.nspname = 'auth';" | grep -q "1 row"; then
  echo "📝 Creating auth.factor_status enum..."
  docker exec core-supabase-db-1 psql -U postgres -c "CREATE TYPE auth.factor_status AS ENUM ('verified', 'unverified');"
  echo "✓ Created auth.factor_status enum"
else
  echo "✓ auth.factor_status enum already exists"
fi

# Check for aal_level enum in auth schema
echo "📝 Checking for aal_level enum in auth schema..."
if ! docker exec core-supabase-db-1 psql -U postgres -c "SELECT 1 FROM pg_type t JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace WHERE t.typname = 'aal_level' AND n.nspname = 'auth';" | grep -q "1 row"; then
  echo "📝 Creating auth.aal_level enum..."
  docker exec core-supabase-db-1 psql -U postgres -c "CREATE TYPE auth.aal_level AS ENUM ('aal1', 'aal2', 'aal3');"
  echo "✓ Created auth.aal_level enum"
else
  echo "✓ auth.aal_level enum already exists"
fi

# Check for code_challenge_method enum in auth schema
echo "📝 Checking for code_challenge_method enum in auth schema..."
if ! docker exec core-supabase-db-1 psql -U postgres -c "SELECT 1 FROM pg_type t JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace WHERE t.typname = 'code_challenge_method' AND n.nspname = 'auth';" | grep -q "1 row"; then
  echo "📝 Creating auth.code_challenge_method enum..."
  docker exec core-supabase-db-1 psql -U postgres -c "CREATE TYPE auth.code_challenge_method AS ENUM ('s256', 'plain');"
  echo "✓ Created auth.code_challenge_method enum"
else
  echo "✓ auth.code_challenge_method enum already exists"
fi

# Check for one_time_token_type enum in auth schema
echo "📝 Checking for one_time_token_type enum in auth schema..."
if ! docker exec core-supabase-db-1 psql -U postgres -c "SELECT 1 FROM pg_type t JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace WHERE t.typname = 'one_time_token_type' AND n.nspname = 'auth';" | grep -q "1 row"; then
  echo "📝 Creating auth.one_time_token_type enum..."
  docker exec core-supabase-db-1 psql -U postgres -c "CREATE TYPE auth.one_time_token_type AS ENUM ('confirmation_token', 'reauthentication_token', 'recovery_token', 'email_change_token_new', 'email_change_token_current', 'phone_change_token');"
  echo "✓ Created auth.one_time_token_type enum"
else
  echo "✓ auth.one_time_token_type enum already exists"
fi

# Restart auth service
echo "📝 Restarting auth service..."
docker compose restart supabase-auth

# Wait for a while to let it start up
echo "⏱️ Waiting for auth service to start..."
sleep 5

# Check auth service logs
echo "📋 Checking auth service logs (last 10 lines)..."
docker logs core-supabase-auth-1 --tail 10

echo "✅ Supabase auth fix completed."
echo "ℹ️ If you still see issues, try restarting all Supabase services with:"
echo "    docker compose down && docker compose up -d"
