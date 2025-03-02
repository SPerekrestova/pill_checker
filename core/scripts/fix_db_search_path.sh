#!/bin/bash
set -e

echo "🔧 Fixing Database Search Path Issues..."

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

# Step 1: Check current search path
echo "📝 Checking current search path..."
docker exec core-supabase-db-1 psql -U postgres -c "SHOW search_path;"

# Step 2: Update search path for database and role
echo "📝 Updating search path to include auth schema..."
docker exec core-supabase-db-1 psql -U postgres -c "ALTER DATABASE postgres SET search_path TO \"\$user\", public, auth;"
docker exec core-supabase-db-1 psql -U postgres -c "ALTER ROLE postgres SET search_path TO \"\$user\", public, auth;"
echo "✓ Search path updated"

# Step 3: Set appropriate permissions
echo "📝 Setting permissions for auth schema..."
docker exec core-supabase-db-1 psql -U postgres -c "GRANT USAGE ON SCHEMA auth TO postgres;"
docker exec core-supabase-db-1 psql -U postgres -c "GRANT EXECUTE ON FUNCTION auth.uid() TO postgres;"
echo "✓ Permissions set"

# Step 4: Test that the auth schema is accessible
echo "📝 Testing auth schema accessibility..."
docker exec core-supabase-db-1 psql -U postgres -c "SELECT auth.uid();"
echo "✓ Auth schema is accessible"

# Step 5: Restart the application
echo "📝 Restarting application..."
docker compose restart app
echo "✓ Application restarted"

echo "✅ Database search path fix completed."
echo "ℹ️ If you still see issues, try restarting all services with:"
echo "    docker compose down && docker compose up -d"
