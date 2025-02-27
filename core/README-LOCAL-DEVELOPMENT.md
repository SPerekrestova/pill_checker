# PillChecker Local Development Guide

This guide explains how to set up the PillChecker application for local development using a self-hosted Supabase instance.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- [Python 3.9+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

## Quick Start

1. Clone the repository (if you haven't already):
   ```bash
   git clone <repository-url>
   cd PillChecker/core
   ```

2. Create a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up local Supabase and the application:
   ```bash
   # Create necessary directories for Supabase volumes
   mkdir -p supabase/volumes/api
   mkdir -p supabase/volumes/storage

   # Create the Kong configuration file
   echo '
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
   ' > supabase/volumes/api/kong.yml

   # Start the services with Docker Compose
   docker-compose up -d
   ```

4. Wait for services to initialize (this may take a minute or two)

5. Access the local services:
   - **PillChecker App**: http://localhost:8000
   - **Supabase Studio**: http://localhost:54323
   - **MailHog (Email Testing)**: http://localhost:8025

## Environment Configuration

The `docker-compose.yml` file includes default environment variables for local development. If you need to customize any settings:

1. Create a `.env.local` file with your custom values:
   ```
   # Override any environment variables here
   SECRET_KEY=your-custom-secret-key
   ```

2. Restart the containers to apply changes:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

## Database Migrations

The project uses Alembic for database migrations. The `scripts/db_management.py` script provides a convenient interface for managing these migrations.

### Initial Database Setup

When starting the project for the first time, you need to apply initial migrations to create the database schema:

```bash
# Run migrations inside the Docker container (recommended)
docker-compose exec app python scripts/db_management.py apply_migrations

# Alternatively, if you need to initialize the database during container startup
# Add this to your docker-compose.yml in the app service
# command: sh -c "sleep 10 && python scripts/db_management.py apply_migrations && uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

### Using the Database Management Script

The `db_management.py` script can be used in two different ways:

#### 1. From Inside the Docker Container (Recommended)

Running the script from inside the Docker container ensures it has the correct environment variables and network access to the Supabase database:

```bash
# Apply migrations
docker-compose exec app python scripts/db_management.py apply_migrations

# Generate a new migration
docker-compose exec app python scripts/db_management.py generate_migration "add user roles"

# Roll back the last migration
docker-compose exec app python scripts/db_management.py rollback

# Roll back multiple migrations
docker-compose exec app python scripts/db_management.py rollback --steps 3

# Export the current schema
docker-compose exec app python scripts/db_management.py export_schema

# Reset the development database (CAUTION: destructive)
docker-compose exec app python scripts/db_management.py reset_database
```

#### 2. From Your Local Machine

If you want to run the script from your local machine, you need to ensure it can connect to the Supabase database:

```bash
# Set environment variables to connect to the database
export APP_ENV=development
export DEV_DATABASE_USER=postgres
export DEV_DATABASE_PASSWORD=postgres
export DEV_DATABASE_HOST=localhost  # Use localhost since the port is mapped
export DEV_DATABASE_PORT=5432
export DEV_DATABASE_NAME=postgres

# Then run the script
python scripts/db_management.py apply_migrations
```

### Automating Initial Schema Creation

There are several ways to automate the initial schema creation:

1. **Custom Entrypoint Script**: Create a custom entrypoint script for the app container:

   ```bash
   # Create an entrypoint.sh file
   echo '#!/bin/sh
   # Wait for database to be ready
   echo "Waiting for database..."
   sleep 10
   
   # Apply migrations
   echo "Applying database migrations..."
   python scripts/db_management.py apply_migrations
   
   # Start the application
   echo "Starting application..."
   exec uvicorn app.main:app --host 0.0.0.0 --port 8000
   ' > entrypoint.sh
   
   # Make it executable
   chmod +x entrypoint.sh
   ```

   Then update your Dockerfile or docker-compose.yml to use this entrypoint.

2. **Using Docker Compose Command Override**:

   In your docker-compose.yml, modify the app service:

   ```yaml
   app:
     build:
       context: .
       dockerfile: Dockerfile
     # ... other configuration ...
     command: >
       sh -c "
         echo 'Waiting for database...' &&
         sleep 10 &&
         echo 'Applying migrations...' &&
         python scripts/db_management.py apply_migrations &&
         echo 'Starting application...' &&
         uvicorn app.main:app --host 0.0.0.0 --port 8000
       "
   ```

3. **Using Docker Healthchecks**:

   In your docker-compose.yml, add healthchecks to ensure the database is ready before starting the app:

   ```yaml
   supabase-db:
     # ... existing configuration ...
     healthcheck:
       test: ["CMD-SHELL", "pg_isready -U postgres"]
       interval: 5s
       timeout: 5s
       retries: 5

   app:
     # ... existing configuration ...
     depends_on:
       supabase-db:
         condition: service_healthy
     command: >
       sh -c "
         echo 'Applying migrations...' &&
         python scripts/db_management.py apply_migrations &&
         echo 'Starting application...' &&
         uvicorn app.main:app --host 0.0.0.0 --port 8000
       "
   ```

## Creating New Migrations

When making changes to the data model:

1. Update the SQLAlchemy models in your code
2. Generate a migration to capture the changes:
   ```bash
   docker-compose exec app python scripts/db_management.py generate_migration "describe your changes"
   ```
3. Review the generated migration file in `migrations/versions/`
4. Apply the migration:
   ```bash
   docker-compose exec app python scripts/db_management.py apply_migrations
   ```
5. Test your changes
6. Commit both code and migration files to version control

## Working with Supabase Locally

### Authentication

When working with local Supabase, all authentication emails are captured by MailHog. Check http://localhost:8025 to view and access signup and password reset emails.

### Storage Buckets

On first run, you'll need to create the storage bucket manually:

1. Go to Supabase Studio at http://localhost:54323
2. Navigate to Storage
3. Create a new bucket called "scans" with public access

### Schema Changes

Best practices for schema changes:

1. Make changes to SQLAlchemy models in code
2. Generate migrations with Alembic
3. Apply migrations
4. Test changes locally
5. Commit both code and migration files to version control

## Troubleshooting

### Container Issues

If you encounter issues with containers:

```bash
# View logs
docker-compose logs -f [service-name]

# Restart a specific service
docker-compose restart [service-name]

# Rebuild and restart everything
docker-compose down
docker-compose up -d --build
```

### Database Reset

To completely reset the local database:

```bash
docker-compose down
docker volume rm core_supabase-db-data
docker-compose up -d
```

### Migration Errors

If you encounter migration errors:

1. Check Alembic history: `docker-compose exec app alembic history`
2. Identify problematic migrations
3. Consider using `alembic stamp` to mark a revision as complete without running it:
   ```bash
   docker-compose exec app alembic stamp <revision_id>
   ```

### Database Connection Issues

If the script can't connect to the database:

1. Check that the Supabase database container is running:
   ```bash
   docker-compose ps supabase-db
   ```

2. Verify the database is accepting connections:
   ```bash
   docker-compose exec supabase-db pg_isready -U postgres
   ```

3. Test a direct connection:
   ```bash
   docker-compose exec supabase-db psql -U postgres -c "SELECT 1"
   ```

## Development Best Practices

1. **Environment Isolation**: Use the local Supabase for development to avoid affecting production data
2. **Migration Testing**: Test migrations thoroughly in the local environment before applying to production
3. **Incremental Changes**: Make small, incremental changes to the schema to simplify rollbacks if needed
4. **Version Control**: Commit migration files along with code changes
5. **Documentation**: Document complex migrations with comments

## Additional Resources

- [Supabase Documentation](https://supabase.io/docs)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

## Database Schema Changes

When you need to make changes to the database schema, follow this workflow:

### 1. Update your SQLAlchemy models

First, modify the SQLAlchemy models in your codebase to reflect the desired schema changes. For example:

```python
# Example: Adding a new field to an existing model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    # New field being added
    verification_code = Column(String, nullable=True)
```

### 2. Generate a migration

Use the `db_management.py` script to generate a migration that captures your model changes:

```bash
docker-compose exec app python scripts/db_management.py generate_migration "add user verification"
```

This will create a new migration file in the `migrations/versions/` directory.

### 3. Review the generated migration

Always review the generated migration file to ensure it correctly represents your intended changes. The migration file will be located at `migrations/versions/<timestamp>_add_user_verification.py`.

The migration file will contain functions for both upgrading (applying) and downgrading (reverting) your changes:

```python
# Example migration file content
def upgrade():
    op.add_column('users', sa.Column('verification_code', sa.String(), nullable=True))

def downgrade():
    op.drop_column('users', 'verification_code')
```

Make any necessary adjustments to the migration file if needed.

### 4. Apply the migration

Once you're satisfied with the migration, apply it to update the database schema:

```bash
docker-compose exec app python scripts/db_management.py apply_migrations
```

### 5. Test your changes

Test that your schema changes work as expected with your application code.

### 6. Commit both model and migration files

When committing your changes to version control, always include both:
- The modified model files
- The new migration file(s)

This ensures that other developers and deployment environments can apply the same schema changes.

### Important Notes

1. **Never delete or modify existing migration files** that have been committed to version control
2. **Keep migrations small and focused** on specific changes for easier debugging
3. **The `initial_schema.py` migration is still required** as it establishes the base schema structure
4. **Run migrations automatically in CI/CD pipelines** to ensure test and production environments stay in sync
5. **Test migrations thoroughly** before deploying to production

### Rolling Back Changes

If you need to revert a migration:

```bash
# Roll back the most recent migration
docker-compose exec app python scripts/db_management.py rollback

# Roll back multiple migrations
docker-compose exec app python scripts/db_management.py rollback --steps 3
```

### Viewing Schema

To export the current database schema to SQL for inspection:

```bash
docker-compose exec app python scripts/db_management.py export_schema
``` 