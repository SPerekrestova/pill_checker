from app.core.database import engine, HOST
from sqlalchemy import text

def verify_database_connection():
    try:
        # Try to connect to the database
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"Successfully connected to the database. PostgreSQL version: {version}")
            return True
    except Exception as e:
        print(f"Failed to connect to the database: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"Attempting to connect to database at: {HOST}")
    verify_database_connection() 