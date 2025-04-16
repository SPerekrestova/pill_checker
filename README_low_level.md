# PillChecker Backend Service Guidelines

## Service Overview
The backend service is a FastAPI application that provides:
- OCR-based medication recognition
- Integration with BiomedNER for ingredient detection
- User authentication via Supabase
- RESTful API endpoints for medication management

## Architecture

### Component Structure
```
app/
├── api/            # API endpoints and routes
├── core/           # Core business logic
├── models/         # SQLAlchemy models
├── schemas/        # Pydantic schemas
├── services/       # Business services
├── utils/          # Utility functions
├── static/         # Static assets
└── templates/      # Jinja2 templates
```

### Architectural Dependency Map
```
                                    External Services
                                   ┌─────────────────┐
                                   │   Supabase      │
                                   │   BiomedNER     │
                                   │   OCR Service   │
                                   └────────┬────────┘
                                           │
                                           ▼
┌─────────────────┐              ┌─────────────────┐
│    API Layer    │              │    Services     │
│  (FastAPI)      │◄────────────►│  Integration    │
│ - Auth          │              │ - Authentication│
│ - Medications   │              │ - Storage       │
└───────┬─────────┘              └────────┬────────┘
        │                                 │
        ▼                                 ▼
┌─────────────────┐              ┌─────────────────┐
│  Data Models    │◄────────────►│    Schemas      │
│  (SQLAlchemy)   │              │   (Pydantic)    │
│ - Medication    │              │ - Validation    │
│ - Profile       │              │ - Serialization │
└───────┬─────────┘              └────────┬────────┘
        │                                 │
        └─────────────────┐   ┌──────────┘
                         ▼   ▼
                   ┌─────────────────┐
                   │    Database     │
                   │   (PostgreSQL)  │
                   └─────────────────┘
```

## API Structure

### Authentication Endpoints (`/api/v1/auth`)
| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/register` | POST | Register a new user | `UserCreate` (email, password, password_confirm, username) | User ID and message |
| `/login` | POST | Log in a user | OAuth2 form (username/password) | `Token` (access_token, token_type, expires_in, refresh_token) |
| `/logout` | POST | Log out a user | None | Success message |
| `/refresh-token` | POST | Refresh an access token | `RefreshToken` (refresh_token) | `Token` (new tokens) |
| `/password-reset/request` | POST | Request a password reset | `EmailRequest` (email) | Success message |
| `/password-reset/verify` | POST | Reset password with token | `PasswordReset` (token, new_password, new_password_confirm) | Success message |
| `/verify-email` | GET | Verify email address | `token` (query param) | Success message |
| `/create-profile` | POST | Create user profile | `ProfileCreate` (username) | Profile details |

### Medication Endpoints (`/api/v1/medications`)
| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/upload` | POST | Upload and process medication image | Image file | `MedicationResponse` |
| `/list` | GET | List user medications | Query params (page, size) | `PaginatedResponse` of medications |
| `/{medication_id}` | GET | Get medication by ID | Path param (medication_id) | `MedicationResponse` |
| `/recent` | GET | Get recent medications | Query param (limit) | List of `MedicationResponse` |

## Database Schema

### Profile Model
- `id` (UUID): Primary key, associated with Supabase user ID
- `username` (Text): Unique display name
- `bio` (Text): User's biography or description
- Relationships:
  - `medications`: One-to-many relationship with Medication model

### Medication Model
- `id` (BigInteger): Primary key
- `profile_id` (UUID): Foreign key to Profile
- `title` (String): Name or title of the medication
- `scan_date` (DateTime): Date when the medication was scanned
- `active_ingredients` (Text): List of active ingredients
- `scanned_text` (Text): Raw text extracted from the scan
- `dosage` (String): Dosage information
- `prescription_details` (JSON): Additional prescription details
- `scan_url` (Text): URL of the uploaded medication scan
- Relationships:
  - `profile`: Many-to-one relationship with Profile model

## UML Class Diagram

```
┌───────────────────────┐       ┌───────────────────────┐
│        Profile        │       │      Medication       │
├───────────────────────┤       ├───────────────────────┤
│ +id: UUID (PK)        │       │ +id: BigInteger (PK)  │
│ +username: String     │  1:N  │ +profile_id: UUID (FK)│
│ +bio: String          │◄──────┤ +title: String        │
├───────────────────────┤       │ +scan_date: DateTime  │
│ +__repr__()           │       │ +active_ingredients:  │
└───────────────────────┘       │  String               │
                                │ +scanned_text: String │
                                │ +dosage: String       │
                                │ +prescription_details:│
                                │  JSON                 │
                                │ +scan_url: String     │
                                ├───────────────────────┤
                                │ +__repr__()           │
                                └───────────────────────┘

┌─────────────────────────┐     ┌────────────────────┐
│     EasyOCRClient       │     │     OCRClient      │
├─────────────────────────┤     ├────────────────────┤
│ -reader: EasyOCR Reader │     │ +read_text(image)  │
├─────────────────────────┤     └────────────────────┘
│ +read_text(image)       │              ▲
└──────────┬──────────────┘              │
           │ implements                  │
           └──────────────────────────────
```

## Setup and Configuration

### Quick Start with Self-hosted Supabase (Recommended)
The quickest way to get started with local development is to use the setup script:

```bash
# Run the setup script to initialize everything
./scripts/setup_dev_environment.sh
```

This will set up:
- Python virtual environment
- Required dependencies
- Local Supabase instance with Docker
- Database migrations
- Storage bucket configuration

For detailed instructions on working with the local Supabase setup, see [README-LOCAL-DEVELOPMENT.md](README-LOCAL-DEVELOPMENT.md).

### Manual Setup
1. **Environment Setup**
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows

   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   ```bash
   # Copy example environment file
   cp .env.example .env

   # Required variables:
   - BIOMED_HOST         # BiomedNER service host
   - BIOMED_SCHEME      # BiomedNER service scheme (http/https)
   - DATABASE_URL       # Database connection string
   - SUPABASE_URL      # Supabase project URL
   - SUPABASE_KEY      # Supabase API key
   ```

## Testing Options

The project includes a comprehensive testing framework with various options for running tests:

### Basic Test Commands
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_models.py

# Run with verbose output
python -m pytest -v
```

### Test Categories

#### 1. Standard Tests (Fast)
These tests use mocked OCR services and run quickly:
```bash
# Skip OCR tests (run only standard tests)
python -m pytest -m "not ocr"
```

#### 2. OCR Tests (Slow)
These tests use the actual OCR implementation and may be slower:
```bash
# Run only OCR tests
python -m pytest -m "ocr"

# Skip OCR tests in CI environments
export SKIP_REAL_OCR_TESTS=True
python -m pytest
```

### Test Image Generation
The project includes utilities to generate test images for OCR testing:
```bash
# Generate test images manually
python tests/test_utils/create_test_image.py [output_directory] [count]
```

### Test Coverage
```bash
# Run with coverage report
pytest --cov=app tests/

# Generate detailed coverage report
pytest --cov=app tests/ && coverage report --show-missing > coverage_report.txt
```

## Database Management

### Using the Database Management Script
The project includes a database management script that makes it easy to manage migrations:

```bash
# Generate a new migration after model changes
python scripts/db_management.py generate_migration "describe your changes"

# Apply pending migrations
python scripts/db_management.py apply_migrations

# Rollback the last migration
python scripts/db_management.py rollback

# Export database schema
python scripts/db_management.py export_schema
```

See [README-LOCAL-DEVELOPMENT.md](README-LOCAL-DEVELOPMENT.md) for detailed instructions on database management.

### Manual Alembic Commands
```bash
# Create a new migration
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1

# View migration history
alembic history --verbose
```

## Supabase Local Development

### Setting Up Local Supabase From Scratch

This project uses Supabase for authentication, database, and storage. Here's how to set up a local Supabase instance:

1. **Install Supabase CLI**
   ```bash
   # Install Supabase CLI (macOS)
   brew install supabase/tap/supabase

   # Install Supabase CLI (Linux/Windows with Homebrew)
   brew install supabase/tap/supabase

   # Or, install using NPM
   npm install -g supabase
   ```

2. **Initialize Supabase Project**
   ```bash
   # Navigate to your project directory
   cd /path/to/project

   # Initialize a new Supabase project
   supabase init
   ```

3. **Start Supabase**
   ```bash
   # Start all Supabase services
   supabase start
   ```

4. **Set Up Database Schema Using Declarative Approach**
   ```bash
   # Create schemas directory if it doesn't exist
   mkdir -p supabase/schemas

   # Create your schema file
   touch supabase/schemas/00_schema.sql

   # Edit the schema file to define your tables
   # Edit supabase/config.toml to set schema_paths = ["./schemas/00_schema.sql"]
   ```

### Creating and Applying Database Migrations

The project uses both Alembic (for migration history) and Supabase's declarative schema approach:

1. **Generate Migrations with Supabase**
   ```bash
   # Stop the database before generating migrations
   supabase stop

   # Generate a migration by diffing your schema against the database
   supabase db diff -f your_migration_name

   # Start Supabase again
   supabase start
   ```

2. **Apply Migrations**
   ```bash
   # Reset database and apply schema
   supabase db reset

   # Apply Alembic migrations to synchronize state
   export DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:54322/postgres
   alembic upgrade head
   ```

3. **Check Migration Status**
   ```bash
   # Check current migration state
   export DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:54322/postgres
   alembic current
   ```

### Working with the Schema

For this project, we recommend using the following workflow:

1. Make changes to your SQLAlchemy models in `app/models/`
2. Generate Alembic migrations using `alembic revision --autogenerate -m "description"`
3. Apply migrations with `alembic upgrade head`
4. If using the declarative schema approach, update `supabase/schemas/00_schema.sql`
5. Generate Supabase migrations with `supabase db diff -f migration_name`

### Resetting the Local Database

If you need to reset your local database completely:

```bash
# Stop Supabase
supabase stop

# Start with a fresh database
supabase start

# Apply Alembic migrations
export DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:54322/postgres
alembic upgrade head
```

### Convenience Scripts

For ease of use, this project includes several convenience scripts:

1. **Set Up Supabase and Migrations**
   ```bash
   # Make script executable if needed
   chmod +x scripts/setup_supabase.sh

   # Run setup script
   ./scripts/setup_supabase.sh
   ```
   This script:
   - Checks Supabase CLI installation
   - Stops any running Supabase instances
   - Starts Supabase with a fresh database
   - Sets the DATABASE_URL environment variable
   - Applies Alembic migrations
   - Verifies the database setup

2. **Generate New Migrations**
   ```bash
   # Make script executable if needed
   chmod +x scripts/generate_migration.sh

   # Generate a new migration
   ./scripts/generate_migration.sh "description_of_changes"
   ```
   This script:
   - Generates an Alembic migration
   - Optionally generates a Supabase migration (requires stopping the database)
   - Guides you through the process of applying migrations

These scripts simplify the database management process and ensure that both Alembic and Supabase migrations stay in sync.

## Development Guidelines
1. **Code Organization**
   - Place API routes in `app/api/v1/`
   - Keep business logic in services
   - Use schemas for request/response validation

2. **API Development**
   - Follow REST principles
   - Document endpoints with FastAPI docstrings
   - Use dependency injection for common functionality

3. **Error Handling**
   - Use custom exceptions from `app/core/exceptions.py`
   - Implement proper error responses
   - Log errors appropriately

## API Documentation
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

## Working with Supabase

The application uses Supabase for:
1. **Authentication**: User signup, login, password reset
2. **Storage**: Storing medication images
3. **Database**: PostgreSQL database for application data

For local development:
- Use the self-hosted Supabase setup described in [README-LOCAL-DEVELOPMENT.md](README-LOCAL-DEVELOPMENT.md)
- Access the Supabase Studio at http://localhost:54323
- Check email notifications in MailHog at http://localhost:8025

## Common Tasks
1. **Adding New Endpoint**
   - Create route in appropriate API module
   - Define request/response schemas
   - Implement service logic
   - Add tests

2. **Database Changes**
   - Update models
   - Generate migration
   - Test migration
   - Update related schemas

3. **External Service Integration**
   - Add service client in `app/services/`
   - Use environment variables for configuration
   - Implement retry logic
   - Add error handling

## Deployment
1. **Docker Build**
   ```bash
   docker build -t pill-checker-pill_checker .
   ```

2. **Docker Run**
   ```bash
   docker run -p 8000:8000 \
     --env-file .env \
     pill-checker-pill_checker
   ```

## Troubleshooting

### Supabase Auth Migration Issues

When running the local Supabase instance, you might encounter issues with the auth service failing to start due to database migration errors:

- `ERROR: type "auth.factor_type" does not exist (SQLSTATE 42704)`
- `ERROR: schema "auth" does not exist (SQLSTATE 3F000)`

We've included a fix script to resolve these issues:

```bash
./scripts/fix_supabase_auth.sh
```

For detailed information about this issue and alternative manual fixes, see the [Troubleshooting Supabase Auth Issues](README-LOCAL-DEVELOPMENT.md#troubleshooting-supabase-auth-issues) section in the Local Development guide.

### Database Search Path Issues

When your application reports errors about missing schemas (like `schema "auth" does not exist`) during migrations or when using RLS policies, even though the schema exists, it's likely a database search path configuration issue.

We've included a fix script to resolve these issues:

```bash
./scripts/fix_db_search_path.sh
```

For detailed instructions on how to fix this issue, see the [Database Search Path Issues](README-LOCAL-DEVELOPMENT.md#database-search-path-issues) section in the Local Development guide.
