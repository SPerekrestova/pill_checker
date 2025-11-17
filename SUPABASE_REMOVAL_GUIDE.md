# Supabase Removal Migration Guide

This document describes the changes made to remove Supabase integration and replace it with custom solutions.

## Overview

The application has been migrated from Supabase to use:
- **FastAPI-Users** for authentication instead of Supabase Auth
- **Local filesystem storage** instead of Supabase Storage
- **SQLAlchemy ORM** for all database operations instead of Supabase PostgREST

## Key Changes

### 1. Authentication System

**Before (Supabase Auth):**
- Used Supabase Auth for user registration/login
- JWT tokens managed by Supabase
- User management through Supabase Admin API

**After (FastAPI-Users):**
- FastAPI-Users for authentication
- Self-managed JWT tokens using python-jose
- User management through SQLAlchemy models

**New Dependencies:**
```python
fastapi-users[sqlalchemy]>=13.0.0
bcrypt>=4.0.0
```

**Removed Dependencies:**
```python
supabase==2.13.0
gotrue>=1.0.0
```

### 2. Storage System

**Before (Supabase Storage):**
- Files uploaded to Supabase Storage buckets
- Public URLs from Supabase CDN

**After (Local Filesystem):**
- Files stored in local `./storage` directory
- Files served through FastAPI static file serving

**Configuration:**
```env
# Old (Removed)
SUPABASE_URL=http://localhost:8000
SUPABASE_KEY=...
SUPABASE_BUCKET_NAME=scans
SUPABASE_SERVICE_ROLE_KEY=...

# New
STORAGE_PATH=./storage
STORAGE_BASE_URL=http://localhost:8000
```

### 3. Database Models

**New Models:**

1. **User Model** (`models/user.py`):
   - Extends FastAPI-Users SQLAlchemyBaseUserTableUUID
   - Fields: id, email, hashed_password, is_active, is_superuser, is_verified
   - One-to-one relationship with Profile

2. **Updated Profile Model** (`models/profile.py`):
   - Added `user_id` foreign key to User table
   - Maintains backward compatibility with existing profile data
   - Relationship with User model

### 4. API Endpoints

**Authentication Endpoints** (`api/v1/auth.py`):

Old endpoints:
- `POST /api/v1/auth/register` - Custom registration
- `POST /api/v1/auth/login` - Custom login
- `POST /api/v1/auth/logout` - Custom logout
- `POST /api/v1/auth/refresh-token` - Token refresh

New endpoints (via FastAPI-Users):
- `POST /api/v1/auth/register` - Standard registration
- `POST /api/v1/auth/register-with-profile` - Registration with profile creation
- `POST /api/v1/auth/jwt/login` - JWT login
- `POST /api/v1/auth/jwt/logout` - JWT logout
- `POST /api/v1/auth/forgot-password` - Password reset request
- `POST /api/v1/auth/reset-password` - Password reset
- `POST /api/v1/auth/request-verify-token` - Email verification request
- `POST /api/v1/auth/verify` - Email verification
- `GET /api/v1/auth/me` - Get current user
- `PATCH /api/v1/auth/users/me` - Update current user

### 5. Services

**New Services:**

1. **Auth Manager** (`services/auth_manager.py`):
   - UserManager for FastAPI-Users
   - JWT strategy configuration
   - Authentication backend setup

2. **Storage Service** (`services/storage.py`):
   - File upload/download operations
   - Local filesystem management
   - Public URL generation

3. **Profile Service** (`services/profile_service.py`):
   - CRUD operations for profiles
   - SQLAlchemy-based implementation

**Removed Services:**
- `services/auth.py` (Supabase-based auth service)

### 6. Database Migrations

**New Migration:** `add_users_table_and_update_profiles.py`

Creates:
- `users` table with FastAPI-Users schema
- `user_id` foreign key in `profiles` table
- Appropriate indexes and constraints

**Migration Steps:**
```bash
# Run migrations
alembic upgrade head

# For existing data, you'll need to:
# 1. Create User records for existing profiles
# 2. Link profiles to users via user_id
```

## Migration Checklist

- [x] Remove Supabase dependencies from `pyproject.toml`
- [x] Add FastAPI-Users dependencies
- [x] Create User model
- [x] Update Profile model with user_id foreign key
- [x] Implement FastAPI-Users authentication
- [x] Create storage service for local filesystem
- [x] Update auth endpoints
- [x] Update medication upload endpoints
- [x] Remove Supabase configuration from settings
- [x] Create database migration for users table
- [x] Update tests (in progress)
- [ ] Update documentation
- [ ] Deploy and test

## Environment Variables

See `.env.example` for the complete list of required environment variables.

**Removed variables:**
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SUPABASE_JWT_SECRET`
- `SUPABASE_BUCKET_NAME`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`

**Added variables:**
- `STORAGE_PATH` - Path to local storage directory
- `STORAGE_BASE_URL` - Base URL for serving files

## Testing

Update test fixtures and mocks to use the new authentication system:

```python
# Old (Supabase)
from tests.conftest import mock_supabase_client

# New (FastAPI-Users)
from tests.conftest import create_test_user
```

## Backwards Compatibility

**Breaking Changes:**
1. Token format changed (Supabase JWT → FastAPI-Users JWT)
2. User ID source changed (Supabase Auth → local users table)
3. Storage URLs changed (Supabase Storage → local storage)

**Data Migration Required:**
- Existing users need to be recreated in the new users table
- Profile.id may need to be updated to match new User.id values
- Uploaded file URLs in database need to be updated

## Deployment Notes

1. **Database Migration:**
   ```bash
   alembic upgrade head
   ```

2. **Create Storage Directory:**
   ```bash
   mkdir -p ./storage
   chmod 755 ./storage
   ```

3. **Update Environment Variables:**
   - Remove all SUPABASE_* variables
   - Add STORAGE_PATH and STORAGE_BASE_URL

4. **User Data Migration:**
   - Export existing user data from Supabase
   - Create corresponding users in new system
   - Update profile.user_id references

## Support

For issues or questions about the migration, please refer to:
- FastAPI-Users documentation: https://fastapi-users.github.io/fastapi-users/
- Project README: README.md
