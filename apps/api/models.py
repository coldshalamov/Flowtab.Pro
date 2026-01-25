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

    # Subscription fields
    is_premium: bool = Field(
        default=True, description="Whether this Flow requires premium subscription"
    )
    featured: bool = Field(default=False, description="Show in free tier preview")
    total_copies: int = Field(default=0, description="Cached total copy count")

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

    # Subscription fields
    stripe_customer_id: str | None = Field(
        default=None, index=True, description="Stripe Customer ID for subscriptions"
    )
    is_creator: bool = Field(
        default=False, description="Whether the user is a content creator"
    )

    # Marketplace fields (creator payouts)
    stripe_connect_id: str | None = Field(
        default=None, index=True, description="Stripe Connect Account ID"
    )
    is_seller: bool = Field(
        default=False, description="Whether the user has enabled selling"
    )


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
    status: str = Field(
        default="pending", index=True
    )  # pending, paid, failed, refunded

    createdAt: datetime = Field(default_factory=datetime.utcnow)


class Subscription(SQLModel, table=True):
    """User subscription state (managed by Stripe webhooks)."""

    __tablename__ = "subscriptions"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_subscription_user"),
        UniqueConstraint("stripe_subscription_id", name="uq_subscription_stripe_id"),
    )

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    user_id: str = Field(foreign_key="users.id", index=True)

    stripe_subscription_id: str = Field(index=True, max_length=255)
    stripe_customer_id: str = Field(max_length=255)

    status: str = Field(max_length=20, index=True)  # active, canceled, past_due, unpaid
    plan_id: str = Field(default="premium_monthly", max_length=50)

    current_period_start: datetime = Field()
    current_period_end: datetime = Field()
    cancel_at_period_end: bool = Field(default=False)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FlowCopy(SQLModel, table=True):
    """Append-only log of Flow copy events for payout calculation."""

    __tablename__ = "flow_copies"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "flow_id", "billing_month", name="uq_copy_user_flow_month"
        ),
    )

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    user_id: str = Field(foreign_key="users.id", index=True)
    flow_id: str = Field(foreign_key="prompts.id", index=True)
    creator_id: str = Field(
        index=True, description="Denormalized for faster aggregation"
    )

    counted_for_payout: bool = Field(
        default=False, description="Whether this copy counts toward creator payout"
    )
    copied_at: datetime = Field(default_factory=datetime.utcnow)
    billing_month: datetime = Field(
        description="First day of billing month (YYYY-MM-01)"
    )


class CreatorPayout(SQLModel, table=True):
    """Monthly aggregated payouts for creators."""

    __tablename__ = "creator_payouts"
    __table_args__ = (
        UniqueConstraint("creator_id", "billing_month", name="uq_payout_creator_month"),
    )

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    creator_id: str = Field(foreign_key="users.id", index=True)
    billing_month: datetime = Field(
        description="First day of billing month (YYYY-MM-01)"
    )

    copy_count: int = Field(default=0)
    amount_cents: int = Field(default=0, description="copy_count * 7 cents")

    status: str = Field(
        default="pending", max_length=20
    )  # pending, processing, paid, failed
    stripe_transfer_id: str | None = Field(default=None)
    paid_at: datetime | None = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Connection Manager Models


class Provider(SQLModel, table=True):
    """AI provider configuration and capabilities."""

    __tablename__ = "providers"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )

    name: str = Field(unique=True, max_length=100, index=True)
    slug: str = Field(unique=True, max_length=100, index=True)
    display_name: str = Field(max_length=100)

    # Provider capabilities
    supports_api_key: bool = Field(default=True)
    supports_oauth: bool = Field(default=False)
    supports_manual: bool = Field(default=True)

    # API configuration
    api_endpoint: str | None = Field(default=None, max_length=500)
    auth_type: str = Field(default="api_key", max_length=50)  # api_key, oauth, manual

    # Provider metadata
    description: str | None = Field(default=None, max_length=500)
    documentation_url: str | None = Field(default=None, max_length=500)

    # Rate limiting
    rate_limit_per_minute: int | None = Field(default=None)
    rate_limit_per_hour: int | None = Field(default=None)

    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AccountConnection(SQLModel, table=True):
    """User's connection to an AI provider."""

    __tablename__ = "account_connections"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )

    user_id: str = Field(foreign_key="users.id", index=True)
    provider_id: str = Field(foreign_key="providers.id", index=True)

    label: str = Field(
        max_length=100, description="User-defined label for this connection"
    )
    connection_type: str = Field(max_length=50, index=True)  # api_key, oauth, manual

    # Status tracking
    status: str = Field(
        default="active", max_length=50, index=True
    )  # active, inactive, error

    # Last usage tracking
    last_used_at: datetime | None = Field(default=None)
    last_error: str | None = Field(default=None, max_length=500)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CredentialVaultItem(SQLModel, table=True):
    """Encrypted credential storage for API connections."""

    __tablename__ = "credential_vault_items"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )

    connection_id: str = Field(foreign_key="account_connections.id", index=True)

    # Encrypted data (format: iv:auth_tag:encrypted_content)
    encrypted_data: str = Field()

    # Metadata
    key_name: str = Field(
        max_length=100, description="Name of the credential key (e.g., 'api_key')"
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ManualOverride(SQLModel, table=True):
    """Manual configuration overrides for provider connections."""

    __tablename__ = "manual_overrides"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )

    connection_id: str = Field(foreign_key="account_connections.id", index=True)

    # JSON configuration for manual overrides
    config: dict = Field(default_factory=dict, sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
