#!/usr/bin/env python
"""
Create Supabase Storage Bucket Script

This script creates a storage bucket in Supabase for the PillChecker application.
It's designed to be run during the application startup process.
"""

import os
import time
import requests


def create_storage_bucket():
    """Create a storage bucket in Supabase if it doesn't already exist."""
    # Wait a bit for storage to be ready
    time.sleep(5)

    # Get environment variables
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    bucket_name = os.environ.get("STORAGE_BUCKET", "scans")

    # Check if required variables are set
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL or SUPABASE_KEY environment variables not set")
        return False

    # Set up headers for Supabase API
    headers = {"apikey": supabase_key, "Authorization": f"Bearer {supabase_key}"}

    try:
        print(f"Attempting to create storage bucket '{bucket_name}'...")

        # Create the storage bucket
        response = requests.post(
            f"{supabase_url}/storage/v1/buckets",
            headers=headers,
            json={"name": bucket_name, "public": True},
        )

        # Check response
        if response.status_code == 200 or response.status_code == 201:
            print("Storage bucket created successfully!")
            return True
        elif response.status_code == 400 and "already exists" in response.text:
            print("Storage bucket already exists!")
            return True
        else:
            print(f"Error creating bucket: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"Exception when creating bucket: {str(e)}")
        return False


if __name__ == "__main__":
    create_storage_bucket()
