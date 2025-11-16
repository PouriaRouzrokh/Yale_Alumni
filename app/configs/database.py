"""Database configuration for ADK session management."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator

# Database path configuration
DATABASE_URL = os.path.join(os.path.dirname(__file__), "../../data/database.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_URL}"

# Remove the existing database file if it exists
if os.path.exists(DATABASE_URL):
    print(f"Removing existing database file at {DATABASE_URL}...")
    os.remove(DATABASE_URL)

# SQLAlchemy engine and session configuration
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """Database dependency for FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
