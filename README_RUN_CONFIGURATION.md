# Running PillChecker in PyCharm

This guide explains how to run the PillChecker application in PyCharm while using Docker for the database and other services.

## Prerequisites

1. Make sure you have Docker and Docker Compose installed on your system.
2. Ensure you have PyCharm Professional (for full Docker integration) or PyCharm Community Edition.
3. Make sure you have Python 3.9 installed and a virtual environment set up for the project.

## Setup Instructions

### Step 1: Start Supabase Services in Docker

Before running the application in PyCharm, you need to start the Supabase services in Docker:

```bash
# Navigate to your project directory
cd /path/to/pill_checker

# Start Supabase using the Supabase CLI
supabase start
```

This will start all the necessary Supabase services, including:
- PostgreSQL database on port 54322
- Supabase API on port 54321
- Storage service
- Authentication service

### Step 2: Run the Application in PyCharm

1. Open the PillChecker project in PyCharm.
2. In the top-right corner, you should see a dropdown with run configurations.
3. Select the "FastAPI" configuration from the dropdown.
4. Click the green "Run" button (or press Shift+F10) to start the application.

The application will start and connect to the Supabase services running in Docker.

### Step 3: Debug the Application (Optional)

If you need to debug the application:

1. In the top-right corner, select the "FastAPI_Debug" configuration from the dropdown.
2. Click the green "Debug" button (or press Shift+F9) to start the application in debug mode.

This configuration enables the DEBUG mode in the application, which provides more detailed error messages and enables the API documentation at `/api/docs` and `/api/redoc`.

## Configuration Details

### FastAPI Configuration

The "FastAPI" run configuration is set up with the following settings:

- **Script path**: `src/pill_checker/main.py`
- **Python interpreter**: The virtual environment's Python interpreter
- **Working directory**: The project root
- **Environment variables**: All necessary environment variables from the `.env` file

### FastAPI_Debug Configuration

The "FastAPI_Debug" configuration includes all the settings from the "FastAPI" configuration, plus:

- **DEBUG**: Set to `True` to enable debug mode
- **Debug mode**: Allows setting breakpoints and stepping through code
- **API Documentation**: Enables the Swagger UI at `/api/docs` and ReDoc at `/api/redoc`

## Troubleshooting

If you encounter any issues:

1. **Database connection errors**: Make sure Supabase is running and the database is accessible on port 54322.
   - If you see an error like `could not translate host name "host.docker.internal" to address: nodename nor servname provided, or not known`, this is because the application is trying to connect to the database using a Docker-specific hostname. The application has been updated to use the `POSTGRES_HOST` environment variable instead, which should be set to `127.0.0.1` when running directly on the host machine.
2. **Missing environment variables**: Check that all required environment variables are set in the run configuration.
3. **Import errors**: Ensure that the PYTHONPATH is set correctly to include the project root.

## Additional Resources

For more information on working with the project, refer to:
- [README.md](README.md) - General project information
- [README_low_level.md](README_low_level.md) - Detailed technical documentation
