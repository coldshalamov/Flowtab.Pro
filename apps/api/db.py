import os
from typing import Generator

from sqlmodel import SQLModel, Session, create_engine

from apps.api.models import Prompt, User, OAuthAccount, Comment, Like
from apps.api.settings import settings

# Use test database URL if TESTING environment variable is set
if os.getenv("TESTING") == "true":
    database_url = "sqlite:///:memory:"
else:
    database_url = settings.database_url

if "sqlite" in database_url:
    connect_args = {"check_same_thread": False}
    engine = create_engine(database_url, connect_args=connect_args, echo=False)
else:
    engine = create_engine(database_url, echo=False)

# Allow overriding the engine for testing
_test_engine = None


def set_test_engine(test_engine):
    """Set the test engine for testing."""
    global _test_engine
    _test_engine = test_engine


def get_engine():
    """Get the current engine (test engine if set, otherwise default engine)."""
    global _test_engine
    return _test_engine if _test_engine else engine


def init_db() -> None:
    """Initialize the database with all tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency for getting a database session."""
    current_engine = get_engine()
    session = Session(current_engine)
    try:
        yield session
    finally:
        session.close()
