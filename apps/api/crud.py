"""
CRUD operations for the Flowtab.Pro backend API.

This module provides database access functions for the Prompt model,
including search, filtering, pagination, and CRUD operations.
"""

import re
from datetime import datetime
from typing import Any

from sqlmodel import Session, select
from sqlalchemy import String, func, or_
from sqlalchemy.sql.expression import cast

from apps.api.models import Prompt, User
from apps.api.schemas import PromptCreate, UserCreate


def get_user_by_email(session: Session, email: str) -> User | None:
    """
    Get a user by email.
    """
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def create_user(
    session: Session, user_create: UserCreate, hashed_password: str
) -> User:
    """
    Create a new user.
    """
    user = User(
        email=user_create.email,
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_prompt_by_slug(session: Session, slug: str) -> Prompt | None:
    """
    Query the database for a prompt by slug.

    Args:
        session: SQLAlchemy database session
        slug: URL-friendly unique identifier

    Returns:
        The prompt if found, None otherwise
    """
    statement = select(Prompt).where(Prompt.slug == slug)
    result = session.exec(statement).first()
    return result


def get_prompts(
    session: Session,
    skip: int = 0,
    limit: int = 100,
    q: str | None = None,
    tags: list[str] | None = None,
    difficulty: str | None = None,
    worksWith: list[str] | None = None,
) -> tuple[list[Prompt], int]:
    """
    Query prompts with filters, search, and pagination.

    Args:
        session: SQLAlchemy database session
        skip: Number of results to skip (for pagination)
        limit: Maximum number of results to return
        q: Search query for text search across title, summary, and promptText
        tags: List of tags to filter by (AND logic - prompts must contain ALL specified tags)
        difficulty: Difficulty level to filter by (exact match)
        worksWith: List of tools to filter by (OR logic - prompts must contain ANY specified tool)

    Returns:
        Tuple of (list of prompts, total count)
    """
    # Start with base query
    statement: Select[tuple[Prompt]] = select(Prompt)

    # Apply text search (ILIKE across title, summary, and promptText)
    if q:
        search_pattern = f"%{q}%"
        statement = statement.where(
            or_(
                Prompt.title.ilike(search_pattern),
                Prompt.summary.ilike(search_pattern),
                Prompt.promptText.ilike(search_pattern),
            )
        )

    # Apply difficulty filter (exact match)
    if difficulty:
        statement = statement.where(Prompt.difficulty == difficulty)

    # Apply tags filter (AND logic - prompts must contain ALL specified tags)
    if tags:
        for tag in tags:
            # For SQLite and PostgreSQL compatibility, filter by checking if tag is in the JSON array
            # Use string-based filtering which works with both databases
            # Escape quotes in the tag value
            escaped_tag = tag.replace('"', '""')
            pattern = '%"' + escaped_tag + '"%'
            statement = statement.where(cast(Prompt.tags, type_=String).like(pattern))

    # Apply worksWith filter (OR logic - prompts must contain ANY specified tool)
    if worksWith:
        # Build OR conditions for each tool
        works_with_conditions = []
        for tool in worksWith:
            # Escape quotes in the tool value
            escaped_tool = tool.replace('"', '""')
            pattern = '%"' + escaped_tool + '"%'
            works_with_conditions.append(
                cast(Prompt.worksWith, type_=String).like(pattern)
            )
        if works_with_conditions:
            statement = statement.where(or_(*works_with_conditions))

    # Get total count before pagination
    # Use a simpler count query to avoid subquery issues
    # Count the ID column instead of using select_from with the statement
    count_statement = select(func.count(Prompt.id))
    # Apply the same filters to the count statement
    if q:
        search_pattern = f"%{q}%"
        count_statement = count_statement.where(
            or_(
                Prompt.title.ilike(search_pattern),
                Prompt.summary.ilike(search_pattern),
                Prompt.promptText.ilike(search_pattern),
            )
        )
    if difficulty:
        count_statement = count_statement.where(Prompt.difficulty == difficulty)
    if tags:
        for tag in tags:
            escaped_tag = tag.replace('"', '""')
            pattern = '%"' + escaped_tag + '"%'
            count_statement = count_statement.where(
                cast(Prompt.tags, type_=String).like(pattern)
            )
    if worksWith:
        works_with_conditions = []
        for tool in worksWith:
            escaped_tool = tool.replace('"', '""')
            pattern = '%"' + escaped_tool + '"%'
            works_with_conditions.append(
                cast(Prompt.worksWith, type_=String).like(pattern)
            )
        if works_with_conditions:
            count_statement = count_statement.where(or_(*works_with_conditions))
    total_count = session.exec(count_statement).one()

    # Apply pagination and ordering
    statement = statement.order_by(Prompt.createdAt.desc()).offset(skip).limit(limit)

    # Execute query
    results = session.exec(statement).all()

    return list(results), total_count


def get_all_tags(session: Session) -> list[str]:
    """
    Query all prompts and collect unique tags.

    Args:
        session: SQLAlchemy database session

    Returns:
        Sorted list of unique tags
    """
    # Get all prompts
    statement = select(Prompt)
    results = session.exec(statement).all()

    # Collect all unique tags
    unique_tags = set()
    for prompt in results:
        if prompt.tags:
            unique_tags.update(prompt.tags)

    # Return sorted list
    return sorted(list(unique_tags))


def slugify_title(title: str) -> str:
    """
    Helper function to generate slug from title.

    Converts title to lowercase, replaces spaces with hyphens,
    and removes special characters.

    Args:
        title: The title to slugify

    Returns:
        URL-friendly slug
    """
    # Convert to lowercase
    slug = title.lower()

    # Replace spaces and underscores with hyphens
    slug = re.sub(r"[\s_]+", "-", slug)

    # Remove special characters except hyphens and alphanumeric
    slug = re.sub(r"[^a-z0-9-]", "", slug)

    # Remove consecutive hyphens
    slug = re.sub(r"-+", "-", slug)

    # Remove leading/trailing hyphens
    slug = slug.strip("-")

    return slug


def create_prompt(session: Session, prompt_create: PromptCreate) -> Prompt:
    """
    Create a new prompt from PromptCreate schema.

    Auto-generates slug from title if not provided.
    Ensures slug uniqueness by appending a number if needed.

    Args:
        session: SQLAlchemy database session
        prompt_create: Pydantic schema with prompt data

    Returns:
        The created prompt
    """
    # Generate slug if not provided
    if prompt_create.slug:
        slug = prompt_create.slug
    else:
        slug = slugify_title(prompt_create.title)

    # Ensure slug uniqueness
    base_slug = slug
    counter = 1
    while get_prompt_by_slug(session, slug) is not None:
        slug = f"{base_slug}-{counter}"
        counter += 1

    # Create new prompt instance (datetime and UUID handled by model defaults)
    prompt = Prompt(
        slug=slug,
        title=prompt_create.title,
        summary=prompt_create.summary,
        difficulty=prompt_create.difficulty,
        worksWith=prompt_create.worksWith or [],
        tags=prompt_create.tags or [],
        targetSites=prompt_create.targetSites or [],
        promptText=prompt_create.promptText,
        steps=prompt_create.steps or [],
        notes=prompt_create.notes if prompt_create.notes else None,
    )

    # Add to session, commit, and refresh
    session.add(prompt)
    session.commit()
    session.refresh(prompt)

    return prompt


def delete_prompt(session: Session, prompt: Prompt) -> None:
    """
    Delete a prompt from the database.

    Args:
        session: SQLAlchemy database session
        prompt: The prompt object to delete
    """
    session.delete(prompt)
    session.commit()
