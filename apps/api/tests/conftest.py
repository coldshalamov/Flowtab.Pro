"""
Pytest configuration and fixtures for API testing.

This module provides shared fixtures for testing the Flowtab.Pro API,
including test database setup, test client, and test data seeding.
"""

import os
from typing import Generator

# Set env vars before importing app/settings (they are instantiated at import time).
os.environ["TESTING"] = "true"
os.environ.setdefault("ADMIN_KEY", "test-admin-key-change-me")

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel

from apps.api.db import init_db
from apps.api.main import app
from apps.api.models import Prompt
from apps.api.settings import Settings

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    return engine


@pytest.fixture(scope="function")
def db_session(test_engine):
    """
    Create a test database session.
    
    Creates tables before each test and drops them after.
    """
    # Set the test engine in db.py
    from apps.api.db import set_test_engine
    set_test_engine(test_engine)
    
    # Create all tables
    SQLModel.metadata.create_all(test_engine)
    
    # Create session (not using context manager so it stays open for client fixture)
    session = Session(test_engine)
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables
        SQLModel.metadata.drop_all(test_engine)
        # Reset test engine
        set_test_engine(None)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a test client with database session override.
    
    Overrides the get_session dependency to use the test database.
    Uses the same session as db_session fixture.
    """
    from apps.api.db import get_session
    
    def override_get_session():
        yield db_session
    
    app.dependency_overrides[get_session] = override_get_session
    
    # Don't use context manager to keep session open
    test_client = TestClient(app)
    yield test_client
    
    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def sample_prompt_data():
    """
    Provide sample prompt data for testing.
    
    Returns a dictionary with all required fields for creating a prompt.
    """
    return {
        "slug": "test-prompt",
        "title": "Test Prompt",
        "summary": "A test prompt for unit testing",
        "difficulty": "beginner",
        "worksWith": ["Chrome", "Firefox"],
        "tags": ["test", "automation"],
        "targetSites": ["example.com"],
        "promptText": "This is a test prompt",
        "steps": ["Step 1", "Step 2", "Step 3"],
        "notes": "Test notes",
    }


@pytest.fixture(scope="function")
def seeded_prompts(db_session):
    """
    Seed the database with test prompts.
    
    Creates 25 prompts with varying properties for testing pagination,
    filtering, and search functionality.
    """
    prompts = []
    difficulties = ["beginner", "intermediate", "advanced"]
    tag_sets = [
        ["git", "workflow"],
        ["automation", "browser"],
        ["testing", "quality"],
        ["deployment", "ci-cd"],
        ["git", "automation"],
    ]
    
    for i in range(25):
        prompt = Prompt(
            slug=f"test-prompt-{i}",
            title=f"Test Prompt {i}",
            summary=f"Summary for test prompt {i}",
            difficulty=difficulties[i % 3],
            worksWith=["Chrome", "Firefox", "Edge"][: (i % 3) + 1],
            tags=tag_sets[i % 5],
            targetSites=[f"site{i}.com"],
            promptText=f"Prompt text for test prompt {i}",
            steps=[f"Step {j}" for j in range(1, 4)],
            notes=f"Notes for test prompt {i}",
        )
        db_session.add(prompt)
        prompts.append(prompt)
    
    db_session.commit()
    
    # Refresh all prompts to get their IDs
    for prompt in prompts:
        db_session.refresh(prompt)
    
    return prompts


@pytest.fixture(scope="function")
def admin_key():
    """
    Provide a valid admin key for testing.
    
    Returns the admin key from settings.
    """
    return Settings().admin_key
