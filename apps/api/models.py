from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime


class Prompt(SQLModel, table=True):
    """Database model for prompts."""

    __tablename__ = "prompts"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique identifier (UUID)",
    )

    slug: str = Field(unique=True, index=True, max_length=255)

    title: str = Field(max_length=500)

    summary: str = Field()

    difficulty: str = Field(max_length=20)

    # JSON fields for arrays - using SQLAlchemy Column with JSON type
    worksWith: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="List of compatible tools/browsers",
    )

    tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="List of tags for categorization",
    )

    targetSites: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="List of target websites",
    )

    promptText: str = Field()

    steps: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Step-by-step instructions",
    )

    notes: str | None = Field(default=None)

    author_id: str | None = Field(
        default=None,
        foreign_key="users.id",
        description="ID of the user who created this prompt",
    )

    createdAt: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )

    updatedAt: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )

    like_count: int = Field(default=0, description="Number of likes")


class OAuthAccount(SQLModel, table=True):
    """Database model for OAuth accounts linked to a user."""

    __tablename__ = "oauth_accounts"
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_oauth_provider_user"),
    )

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique identifier (UUID)",
    )

    user_id: str = Field(
        foreign_key="users.id",
        index=True,
        description="User ID owning this OAuth account",
    )

    provider: str = Field(index=True, max_length=32)
    provider_user_id: str = Field(index=True, max_length=255)

    email: str | None = Field(default=None, max_length=255)
    name: str | None = Field(default=None, max_length=255)

    createdAt: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )


class Comment(SQLModel, table=True):
    """Forum comment attached to a prompt."""

    __tablename__ = "comments"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique identifier (UUID)",
    )

    prompt_id: str = Field(
        foreign_key="prompts.id",
        index=True,
        description="Prompt ID this comment belongs to",
    )

    author_id: str = Field(
        foreign_key="users.id",
        index=True,
        description="User ID who wrote the comment",
    )

    body: str = Field(description="Comment body")
    author: "User" = Relationship(back_populates="comments")

    createdAt: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )

    like_count: int = Field(default=0, description="Number of likes")


class Like(SQLModel, table=True):
    """A user's like on a prompt (flow) or comment."""

    __tablename__ = "likes"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "target_type", "target_id", name="uq_like_user_target"
        ),
    )

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique identifier (UUID)",
    )

    user_id: str = Field(foreign_key="users.id", index=True)
    target_type: str = Field(index=True, max_length=16)  # prompt | comment
    target_id: str = Field(index=True)

    createdAt: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )


class User(SQLModel, table=True):
    """Database model for users."""

    __tablename__ = "users"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique identifier (UUID)",
    )
    email: str = Field(unique=True, index=True, max_length=255)
    username: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field()
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)

    createdAt: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    comments: list["Comment"] = Relationship(back_populates="author")
