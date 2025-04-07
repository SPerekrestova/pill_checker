"""Database configuration and session management."""

from typing import Generator

from sqlalchemy import NullPool, create_engine
from sqlalchemy.orm import Session, sessionmaker

from .config import settings
from .logging_config import logger

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    poolclass=NullPool,
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """Get a database session."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.error(f"Database session error: {e}")
        session.rollback()
        raise
    finally:
        session.close()
