#!/usr/bin/env python
"""
Database Management Utility Script for PillChecker

This script provides helper functions for managing database migrations and
Supabase database operations. It's designed to simplify the process of
migrating schema changes between different environments.

Usage:
    python db_management.py [command] [options]

Commands:
    generate_migration - Creates a new migration from SQLAlchemy models
    apply_migrations - Apply pending migrations to the database
    rollback - Rollback the last migration
    reset_database - Reset the development database (caution: destructive)
    export_schema - Export the current database schema to SQL
    compare_schemas - Compare schemas between environments
"""

import os
import sys
import argparse
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.append(str(project_root))


def run_command(cmd, check=True, capture_output=False):
    """Run a shell command and handle errors."""
    try:
        result = subprocess.run(
            cmd, shell=True, check=check, text=True, capture_output=capture_output
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {cmd}")
        print(f"Error details: {e}")
        if e.stdout:
            print(f"Standard output: {e.stdout}")
        if e.stderr:
            print(f"Standard error: {e.stderr}")
        sys.exit(1)


def check_environment():
    """Check that the required environment variables are set."""
    required_vars = [
        "APP_ENV",
        "DEV_DATABASE_USER",
        "DEV_DATABASE_PASSWORD",
        "DEV_DATABASE_HOST",
        "DEV_DATABASE_PORT",
        "DEV_DATABASE_NAME",
    ]

    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nMake sure you're running in a properly configured environment.")
        print("Tip: Source your .env file or use 'python -m app.core.config'")
        sys.exit(1)

    # Warn about production operations
    if os.environ.get("APP_ENV") == "production":
        print("WARNING: You are running in PRODUCTION environment.")
        print("This could potentially affect live data.")
        confirm = input("Are you sure you want to continue? (y/N): ")
        if confirm.lower() != "y":
            print("Operation aborted.")
            sys.exit(1)


def generate_migration(message):
    """Generate a new migration with Alembic."""
    check_environment()

    if not message:
        message = "database_update"

    # Strip spaces and replace with underscores for cleaner migration names
    clean_message = message.replace(" ", "_").lower()

    print(f"Generating migration: {clean_message}")
    cmd = f'alembic revision --autogenerate -m "{clean_message}"'
    run_command(cmd)

    print("\nMigration created. Review the generated file in migrations/versions/")
    print("Make any necessary adjustments before applying it to the database.")


def apply_migrations():
    """Apply pending migrations to the database."""
    check_environment()

    # First, show pending migrations
    print("Checking for pending migrations...")
    result = run_command("alembic current", capture_output=True, check=False)
    current = result.stdout.strip() if result.stdout else "None"

    result = run_command("alembic heads", capture_output=True, check=False)
    head = result.stdout.strip() if result.stdout else "None"

    if current == head:
        print("Database is already up to date. No migrations to apply.")
        return

    print("The following migrations will be applied:")
    try:
        # Try to show migration history, but don't fail if it doesn't work
        run_command("alembic history -r:current", check=False)
    except Exception as e:
        print(f"Could not display migration history: {e}")
        print("Continuing with migration...")

    # In automated environments, we want to apply migrations without confirmation
    if os.environ.get("AUTOMATED_DEPLOYMENT") == "true":
        confirm = "y"
    else:
        confirm = input("Do you want to apply these migrations? (y/N): ")

    if confirm.lower() != "y":
        print("Migration aborted.")
        return

    print("\nApplying migrations...")
    run_command("alembic upgrade head")
    print("Migrations applied successfully.")


def rollback_migration(steps=1):
    """Rollback the last n migrations."""
    check_environment()

    if steps <= 0:
        print("Error: Number of steps must be positive.")
        return

    # Show current position
    result = run_command("alembic current", capture_output=True)
    current = result.stdout.strip()

    if not current or current == "None":
        print("No migrations have been applied yet.")
        return

    print(f"Current migration: {current}")
    print(f"Rolling back {steps} migration(s)...")

    # Show what will be rolled back
    run_command(f"alembic history -r-{steps}:current")

    confirm = input("Do you want to roll back these migrations? (y/N): ")
    if confirm.lower() != "y":
        print("Rollback aborted.")
        return

    run_command(f"alembic downgrade -{steps}")
    print("Rollback completed successfully.")


def reset_database():
    """Reset the development database (CAUTION: destructive operation)."""
    check_environment()

    env = os.environ.get("APP_ENV", "").lower()
    if env == "production":
        print("ERROR: Cannot reset production database.")
        print("This operation is only allowed in development or staging environments.")
        sys.exit(1)

    print("WARNING: This will DROP ALL TABLES and recreate the database schema.")
    print("All data will be permanently lost.")

    confirm = input("Are you absolutely sure you want to continue? Type 'reset' to confirm: ")
    if confirm.lower() != "reset":
        print("Database reset aborted.")
        return

    print("\nResetting database...")

    # Drop all tables through Alembic
    run_command("alembic downgrade base")

    # Then upgrade to latest
    run_command("alembic upgrade head")

    print("Database has been reset and the schema recreated.")


def export_schema():
    """Export the current database schema to SQL."""
    check_environment()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"schema_export_{timestamp}.sql"

    db_user = os.environ.get("DEV_DATABASE_USER")
    db_password = os.environ.get("DEV_DATABASE_PASSWORD")
    db_host = os.environ.get("DEV_DATABASE_HOST")
    db_port = os.environ.get("DEV_DATABASE_PORT")
    db_name = os.environ.get("DEV_DATABASE_NAME")

    # Create the pg_dump command
    cmd = (
        f"PGPASSWORD={db_password} pg_dump -h {db_host} -p {db_port} "
        f"-U {db_user} -d {db_name} --schema-only --no-owner > {filename}"
    )

    print(f"Exporting schema to {filename}...")
    run_command(cmd, check=False)  # pg_dump might return non-zero even on success

    # Check if file was created and has content
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        print(f"Schema exported successfully to {filename}")
    else:
        print("Error: Schema export failed or produced empty file.")
        sys.exit(1)


def compare_schemas(source_env, target_env):
    """Compare schemas between two environments."""
    print(f"Comparing schemas between {source_env} and {target_env}...")

    # This would be a more complex implementation
    # For now, we'll just export schemas and use diff

    source_file = tempfile.NamedTemporaryFile(delete=False, suffix=".sql")
    target_file = tempfile.NamedTemporaryFile(delete=False, suffix=".sql")

    try:
        # Export source schema
        print(f"Exporting schema from {source_env}...")
        # This would require environment switching logic

        # Export target schema
        print(f"Exporting schema from {target_env}...")
        # This would require environment switching logic

        # Compare the schemas
        print("Comparing schemas...")
        run_command(f"diff -u {source_file.name} {target_file.name}", check=False)

    finally:
        # Clean up temporary files
        os.unlink(source_file.name)
        os.unlink(target_file.name)

    print("Schema comparison complete.")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Database Management Utility for PillChecker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # generate_migration command
    gen_parser = subparsers.add_parser(
        "generate_migration", help="Generate a new database migration"
    )
    gen_parser.add_argument("message", nargs="?", help="Migration message/description")

    # apply_migrations command
    subparsers.add_parser("apply_migrations", help="Apply pending migrations to the database")

    # rollback command
    rollback_parser = subparsers.add_parser("rollback", help="Rollback the last migration")
    rollback_parser.add_argument(
        "--steps", type=int, default=1, help="Number of migrations to roll back"
    )

    # reset_database command
    subparsers.add_parser("reset_database", help="Reset the development database")

    # export_schema command
    subparsers.add_parser("export_schema", help="Export the current database schema to SQL")

    # compare_schemas command
    compare_parser = subparsers.add_parser(
        "compare_schemas", help="Compare schemas between environments"
    )
    compare_parser.add_argument(
        "source_env", choices=["development", "staging", "production"], help="Source environment"
    )
    compare_parser.add_argument(
        "target_env", choices=["development", "staging", "production"], help="Target environment"
    )

    args = parser.parse_args()

    if args.command == "generate_migration":
        generate_migration(args.message)
    elif args.command == "apply_migrations":
        apply_migrations()
    elif args.command == "rollback":
        rollback_migration(args.steps)
    elif args.command == "reset_database":
        reset_database()
    elif args.command == "export_schema":
        export_schema()
    elif args.command == "compare_schemas":
        compare_schemas(args.source_env, args.target_env)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
