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
    
    # Type: 'prompt' or 'discussion'
    type: str = Field(default="prompt", index=True, max_length=20)



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
    saves_count: int = Field(default=0, description="Number of bookmarks")
    
    # Marketplace fields
    price: int = Field(default=0, description="Price in cents (0 = free)")
    currency: str = Field(default="usd", max_length=3)


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
    
    # Marketplace fields
    stripe_connect_id: str | None = Field(default=None, index=True, description="Stripe Connect Account ID")
    is_seller: bool = Field(default=False, description="Whether the user has enabled selling")


class Save(SQLModel, table=True):
    """A user's bookmark of a prompt."""
    
    __tablename__ = "saves"
    __table_args__ = (
        UniqueConstraint("user_id", "prompt_id", name="uq_save_user_prompt"),
    )

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    user_id: str = Field(foreign_key="users.id", index=True)
    prompt_id: str = Field(foreign_key="prompts.id", index=True)
    createdAt: datetime = Field(default_factory=datetime.utcnow)


class Purchase(SQLModel, table=True):
    """Record of a prompt purchase."""
    
    __tablename__ = "purchases"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    buyer_id: str = Field(foreign_key="users.id", index=True)
    seller_id: str = Field(foreign_key="users.id", index=True)
    prompt_id: str = Field(foreign_key="prompts.id", index=True)
    
    amount_cents: int = Field(description="Total amount charged in cents")
    platform_fee_cents: int = Field(description="Fee taken by platform in cents")
    currency: str = Field(default="usd", max_length=3)
    
    stripe_payment_intent_id: str = Field(index=True)
    status: str = Field(default="pending", index=True) # pending, paid, failed, refunded
    
    createdAt: datetime = Field(default_factory=datetime.utcnow)
