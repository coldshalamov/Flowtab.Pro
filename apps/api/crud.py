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
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import cast

from apps.api.models import (
    Prompt, User, Comment, Like, Subscription,
    FlowCopy, CreatorPayout, Save
)
from apps.api.schemas import PromptCreate, UserCreate


def get_user_by_email(session: Session, email: str) -> User | None:
    """
    Get a user by email.
    """
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_user_by_username(session: Session, username: str) -> User | None:
    """
    Get a user by username.
    """
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()


def get_user_by_email_or_username(session: Session, login: str) -> User | None:
    """
    Get a user by email or username.
    """
    statement = select(User).where(or_(User.email == login, User.username == login))
    return session.exec(statement).first()


def create_user(
    session: Session, user_create: UserCreate, hashed_password: str
) -> User:
    """
    Create a new user.
    """
    user = User(
        email=user_create.email,
        username=user_create.username,
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
    type_: str | None = None,
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
    
    # Apply type filter
    if type_:
        statement = statement.where(Prompt.type == type_)


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

    if type_:
        count_statement = count_statement.where(Prompt.type == type_)

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


def create_prompt(
    session: Session, prompt_create: PromptCreate, author_id: str | None = None
) -> Prompt:
    """
    Create a new prompt from PromptCreate schema.

    Auto-generates slug from title if not provided.
    Ensures slug uniqueness by appending a number if needed.

    Args:
        session: SQLAlchemy database session
        prompt_create: Pydantic schema with prompt data
        author_id: ID of the user creating the prompt

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

        worksWith=prompt_create.worksWith or [],
        tags=prompt_create.tags or [],
        targetSites=prompt_create.targetSites or [],
        promptText=prompt_create.promptText,
        steps=prompt_create.steps or [],
        notes=prompt_create.notes if prompt_create.notes else None,
        price=prompt_create.price or 0,
        type=prompt_create.type,
        author_id=author_id,
    )

    # Add to session, commit, and refresh
    session.add(prompt)
    session.commit()
    session.refresh(prompt)

    return prompt


def update_prompt(
    session: Session, prompt: Prompt, prompt_update: Any
) -> Prompt:
    """
    Update an existing prompt with data from PromptUpdate schema.

    Args:
        session: SQLAlchemy database session
        prompt: The existing prompt object to update
        prompt_update: Pydantic schema with update data

    Returns:
        The updated prompt
    """
    update_data = prompt_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(prompt, field, value)

    prompt.updatedAt = datetime.utcnow()

    session.add(prompt)
    session.commit()
    session.refresh(prompt)

    return prompt


from sqlalchemy.orm import joinedload

def get_comments_for_prompt(session: Session, prompt_id: str) -> list[Comment]:
    statement = (
        select(Comment)
        .where(Comment.prompt_id == prompt_id)
        .options(joinedload(Comment.author))
        .order_by(Comment.createdAt.asc())
    )
    return list(session.exec(statement).all())


def create_comment(
    session: Session, *, prompt_id: str, author_id: str, body: str
) -> Comment:
    comment = Comment(prompt_id=prompt_id, author_id=author_id, body=body)
    session.add(comment)
    
    # Increment prompt comment count
    from apps.api.models import Prompt
    prompt = session.get(Prompt, prompt_id)
    if prompt:
        prompt.comment_count = (prompt.comment_count or 0) + 1
        session.add(prompt)
    
    session.commit()
    session.refresh(comment)
    return comment


def get_comment_by_id(session: Session, comment_id: str) -> Comment | None:
    statement = select(Comment).where(Comment.id == comment_id)
    return session.exec(statement).first()


def delete_comment(session: Session, comment: Comment) -> None:
    # Decrement prompt comment count
    from apps.api.models import Prompt
    prompt = session.get(Prompt, comment.prompt_id)
    if prompt and prompt.comment_count and prompt.comment_count > 0:
        prompt.comment_count -= 1
        session.add(prompt)
    
    session.delete(comment)
    session.commit()


def get_like(
    session: Session, *, user_id: str, target_type: str, target_id: str
) -> Like | None:
    statement = select(Like).where(
        Like.user_id == user_id,
        Like.target_type == target_type,
        Like.target_id == target_id,
    )
    return session.exec(statement).first()


def like_target(
    session: Session, *, user_id: str, target_type: str, target_id: str
) -> bool:
    """Ensure a like exists. Returns True if a new like was created."""

    like = Like(user_id=user_id, target_type=target_type, target_id=target_id)
    session.add(like)
    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False


def unlike_target(
    session: Session, *, user_id: str, target_type: str, target_id: str
) -> bool:
    """Ensure a like is removed. Returns True if a like was deleted."""

    like = get_like(
        session,
        user_id=user_id,
        target_type=target_type,
        target_id=target_id,
    )
    if not like:
        return False

    session.delete(like)
    session.commit()
    return True


def delete_prompt(session: Session, prompt: Prompt) -> None:
    """
    Delete a prompt from the database.

    Args:
        session: SQLAlchemy database session
        prompt: The prompt object to delete
    """
    session.delete(prompt)
    session.commit()


from apps.api.models import Save

def get_save(session: Session, *, user_id: str, prompt_id: str) -> Save | None:
    statement = select(Save).where(
        Save.user_id == user_id,
        Save.prompt_id == prompt_id,
    )
    return session.exec(statement).first()


def save_prompt(session: Session, *, user_id: str, prompt_id: str) -> bool:
    """Ensure a bookmark (save) exists. Returns True if a new save was created."""
    save = Save(user_id=user_id, prompt_id=prompt_id)
    session.add(save)
    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False


def unsave_prompt(session: Session, *, user_id: str, prompt_id: str) -> bool:
    """Ensure a bookmark (save) is removed. Returns True if removed."""
    save = get_save(session, user_id=user_id, prompt_id=prompt_id)
    if not save:
        return False

    session.delete(save)
    session.commit()
    return True


# Subscription CRUD

def get_subscription_by_user(session: Session, user_id: str) -> Subscription | None:
    """Get subscription for a user."""
    statement = select(Subscription).where(Subscription.user_id == user_id)
    return session.exec(statement).first()


def get_subscription_by_stripe_id(session: Session, stripe_id: str) -> Subscription | None:
    """Get subscription by Stripe subscription ID."""
    statement = select(Subscription).where(
        Subscription.stripe_subscription_id == stripe_id
    )
    return session.exec(statement).first()


def create_or_update_subscription(
    session: Session,
    user_id: str,
    stripe_subscription_id: str,
    stripe_customer_id: str,
    status: str,
    current_period_start: datetime,
    current_period_end: datetime,
    plan_id: str = "premium_monthly",
) -> Subscription:
    """Create or update a subscription."""
    subscription = get_subscription_by_user(session, user_id)

    if subscription:
        subscription.stripe_subscription_id = stripe_subscription_id
        subscription.stripe_customer_id = stripe_customer_id
        subscription.status = status
        subscription.current_period_start = current_period_start
        subscription.current_period_end = current_period_end
        subscription.plan_id = plan_id
        subscription.updated_at = datetime.utcnow()
    else:
        subscription = Subscription(
            user_id=user_id,
            stripe_subscription_id=stripe_subscription_id,
            stripe_customer_id=stripe_customer_id,
            status=status,
            plan_id=plan_id,
            current_period_start=current_period_start,
            current_period_end=current_period_end,
        )

    session.add(subscription)
    session.commit()
    session.refresh(subscription)
    return subscription


def cancel_subscription(session: Session, subscription_id: str) -> Subscription:
    """Cancel a subscription."""
    statement = select(Subscription).where(Subscription.id == subscription_id)
    subscription = session.exec(statement).first()

    if subscription:
        subscription.status = "canceled"
        subscription.cancel_at_period_end = True
        subscription.updated_at = datetime.utcnow()
        session.add(subscription)
        session.commit()
        session.refresh(subscription)

    return subscription


# Flow Copy CRUD

def get_billing_month_start(date: datetime | None = None) -> datetime:
    """Get first day of billing month for a given date (or today)."""
    if date is None:
        date = datetime.utcnow()
    return datetime(date.year, date.month, 1)


def count_copies_this_month(session: Session, user_id: str) -> int:
    """Count total copies a user has made this month."""
    billing_month = get_billing_month_start()
    statement = select(func.count(FlowCopy.id)).where(
        FlowCopy.user_id == user_id,
        FlowCopy.billing_month == billing_month,
        FlowCopy.counted_for_payout == True
    )
    return session.exec(statement).one() or 0


def get_copies_this_month(
    session: Session, user_id: str, billing_month: datetime | None = None
) -> list[FlowCopy]:
    """Get all copies made by user this month."""
    if billing_month is None:
        billing_month = get_billing_month_start()

    statement = select(FlowCopy).where(
        FlowCopy.user_id == user_id,
        FlowCopy.billing_month == billing_month
    )
    return list(session.exec(statement).all())


def has_copied_this_month(
    session: Session, user_id: str, flow_id: str
) -> bool:
    """Check if user has already copied this flow this month."""
    billing_month = get_billing_month_start()
    statement = select(FlowCopy).where(
        FlowCopy.user_id == user_id,
        FlowCopy.flow_id == flow_id,
        FlowCopy.billing_month == billing_month
    )
    return session.exec(statement).first() is not None


def record_flow_copy(
    session: Session,
    user_id: str,
    flow_id: str,
    creator_id: str,
    counted_for_payout: bool = False,
) -> FlowCopy:
    """Record a flow copy event (append-only log)."""
    billing_month = get_billing_month_start()

    # Check if already copied
    if has_copied_this_month(session, user_id, flow_id):
        raise ValueError(
            f"User {user_id} has already copied Flow {flow_id} this month"
        )

    copy = FlowCopy(
        user_id=user_id,
        flow_id=flow_id,
        creator_id=creator_id,
        billing_month=billing_month,
        counted_for_payout=counted_for_payout,
    )

    session.add(copy)
    session.commit()
    session.refresh(copy)
    return copy


def get_flow_copy_by_id(session: Session, copy_id: str) -> FlowCopy | None:
    """Get a flow copy by ID."""
    statement = select(FlowCopy).where(FlowCopy.id == copy_id)
    return session.exec(statement).first()


# Creator Payout CRUD

def get_or_create_payout(
    session: Session, creator_id: str, billing_month: datetime
) -> CreatorPayout:
    """Get or create a payout record for a creator."""
    statement = select(CreatorPayout).where(
        CreatorPayout.creator_id == creator_id,
        CreatorPayout.billing_month == billing_month
    )
    payout = session.exec(statement).first()

    if not payout:
        payout = CreatorPayout(
            creator_id=creator_id,
            billing_month=billing_month,
        )
        session.add(payout)
        session.commit()
        session.refresh(payout)

    return payout


def get_payouts_for_creator(
    session: Session, creator_id: str, limit: int = 12
) -> list[CreatorPayout]:
    """Get recent payouts for a creator."""
    statement = (
        select(CreatorPayout)
        .where(CreatorPayout.creator_id == creator_id)
        .order_by(CreatorPayout.billing_month.desc())
        .limit(limit)
    )
    return list(session.exec(statement).all())


def update_payout_status(
    session: Session,
    payout_id: str,
    status: str,
    stripe_transfer_id: str | None = None,
) -> CreatorPayout:
    """Update payout status."""
    statement = select(CreatorPayout).where(CreatorPayout.id == payout_id)
    payout = session.exec(statement).first()

    if payout:
        payout.status = status
        if stripe_transfer_id:
            payout.stripe_transfer_id = stripe_transfer_id
        if status == "paid":
            payout.paid_at = datetime.utcnow()
        payout.updated_at = datetime.utcnow()
        session.add(payout)
        session.commit()
        session.refresh(payout)

    return payout


def get_total_earnings(session: Session, creator_id: str) -> int:
    """Get total earnings in cents for a creator (from paid payouts)."""
    statement = select(func.sum(CreatorPayout.amount_cents)).where(
        CreatorPayout.creator_id == creator_id,
        CreatorPayout.status == "paid"
    )
    total = session.exec(statement).one()
    return total or 0
