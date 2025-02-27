#!/bin/bash
# Application startup script for PillChecker
# This script handles initialization tasks before starting the FastAPI application

set -e  # Exit immediately if a command exits with a non-zero status

echo "Waiting for all services to be ready..."

# Apply database migrations
echo "Applying database migrations..."
python scripts/db_management.py apply_migrations

# Create storage bucket
echo "Creating storage bucket..."
python scripts/create_bucket.py

# Start the FastAPI application
echo "Starting application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 