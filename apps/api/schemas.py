from __future__ import annotations
from datetime import datetime
from typing import Literal

import re
from html import escape

from pydantic import BaseModel, Field, field_validator


class PromptCreate(BaseModel):
    """
    Schema for creating a new prompt.

    Used for POST /v1/prompts endpoint. All fields are required except
    slug, which can be auto-generated from the title.
    """

    slug: str | None = Field(
        default=None,
        description="URL-friendly unique identifier (optional, auto-generated from title if not provided)",
        max_length=255,
    )

    title: str = Field(
        description="Human-readable title of the prompt",
        min_length=1,
        max_length=500,
    )

    summary: str = Field(
        description="Brief description of what the prompt does",
        min_length=1,
    )



    worksWith: list[str] = Field(
        default_factory=list,
        description="List of compatible tools/browsers",
    )

    tags: list[str] = Field(
        default_factory=list,
        description="List of tags for categorization",
    )

    targetSites: list[str] = Field(
        default_factory=list,
        description="List of target websites this prompt works with",
    )

    promptText: str = Field(
        description="The actual prompt text to be used",
        min_length=1,
    )
    
    type: Literal["prompt", "discussion"] = Field(
        default="prompt",
        description="Type of content: 'prompt' or 'discussion'",
    )

    steps: list[str] = Field(
        default_factory=list,
        description="Step-by-step instructions",
    )

    notes: str = Field(
        default="",
        description="Additional notes or warnings",
    )

    price: int = Field(
        default=0,
        description="Price in cents (0 = free)",
        ge=0,
    )


class PromptUpdate(BaseModel):
    """
    Schema for updating an existing prompt.
    All fields are optional.
    """

    title: str | None = Field(default=None, max_length=500)
    summary: str | None = Field(default=None)

    worksWith: list[str] | None = Field(default=None)
    tags: list[str] | None = Field(default=None)
    targetSites: list[str] | None = Field(default=None)
    promptText: str | None = Field(default=None)
    steps: list[str] | None = Field(default=None)
    notes: str | None = Field(default=None)
    price: int | None = Field(default=None, ge=0)


class PromptRead(BaseModel):
    """
    Schema for reading a prompt.

    Used for GET responses. Contains all prompt fields including
    auto-generated fields like id, createdAt, and updatedAt.
    """

    id: str = Field(description="Unique identifier for the prompt")

    slug: str = Field(description="URL-friendly unique identifier")

    title: str = Field(description="Human-readable title of the prompt")

    summary: str = Field(description="Brief description of what the prompt does")
    
    type: str = Field(description="Type of content")



    worksWith: list[str] = Field(
        description="List of compatible tools/browsers",
    )

    tags: list[str] = Field(
        description="List of tags for categorization",
    )

    targetSites: list[str] = Field(
        description="List of target websites this prompt works with",
    )

    promptText: str = Field(
        description="The actual prompt text to be used",
    )

    steps: list[str] = Field(
        description="Step-by-step instructions",
    )

    notes: str | None = Field(
        default=None,
        description="Additional notes or warnings",
    )

    author_id: str | None = Field(
        default=None,
        description="ID of the user who created this prompt",
    )

    createdAt: datetime = Field(
        description="ISO 8601 timestamp when the prompt was created",
    )

    updatedAt: datetime = Field(
        description="ISO 8601 timestamp when the prompt was last updated",
    )

    like_count: int = Field(
        default=0,
        description="Number of likes",
    )

    saves_count: int = Field(
        default=0,
        description="Number of bookmarks",
    )

    price: int = Field(
        default=0,
        description="Price in cents",
    )

    currency: str = Field(
        default="usd",
        description="Currency code",
    )

    class Config:
        from_attributes = True


class PromptListResponse(BaseModel):
    """
    Schema for paginated list of prompts.

    Used for GET /v1/prompts response.
    """

    items: list[PromptRead] = Field(description="List of prompts")

    page: int = Field(
        ge=1,
        description="Current page number",
    )

    pageSize: int = Field(
        ge=1,
        le=100,
        description="Number of items per page",
    )

    total: int = Field(
        ge=0,
        description="Total number of prompts matching the query",
    )


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=5000)

    @field_validator("body")
    @classmethod
    def validate_body(cls, v: str) -> str:
        # Normalize and reduce control characters.
        v = v.strip()
        v = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", v)

        # Escape HTML so the frontend can safely render as text even if it
        # accidentally uses an unsafe rendering path.
        return escape(v, quote=False)


class CommentRead(BaseModel):
    id: str
    prompt_id: str
    author_id: str
    author: UserPublic | None = None
    body: str
    createdAt: datetime
    like_count: int = 0

    class Config:
        from_attributes = True


class LikeStatusResponse(BaseModel):
    liked: bool
    likeCount: int


class CommentListResponse(BaseModel):
    items: list[CommentRead]


class TagsResponse(BaseModel):
    """
    Schema for list of all available tags.

    Used for GET /v1/tags response.
    """

    items: list[str] = Field(description="List of all available tags")


class ErrorDetail(BaseModel):
    """
    Schema for a single validation error detail.

    Used within ValidationError to describe individual field errors.
    """

    field: str = Field(description="Field that failed validation")

    message: str = Field(description="Specific validation error message")


class ErrorResponse(BaseModel):
    """
    Schema for error responses.

    Used for general error responses across all endpoints.
    """

    error: str = Field(description="Error type or category")

    message: str = Field(description="Human-readable error message")


class ValidationError(ErrorResponse):
    """
    Schema for validation error responses.

    Extends ErrorResponse with details about specific field validation errors.
    Used for 422 Unprocessable Entity responses.
    """

    details: list[ErrorDetail] = Field(
        default_factory=list,
        description="List of validation errors",
    )


class UserBase(BaseModel):
    username: str = Field(description="Unique username for display and login", min_length=3, max_length=50)


class UserCreate(UserBase):
    email: str = Field(description="User email address")
    password: str = Field(description="User password", min_length=8)


class UserRead(UserBase):
    id: str
    email: str
    is_active: bool
    is_superuser: bool
    createdAt: datetime

    class Config:
        from_attributes = True


class UserPublic(BaseModel):
    id: str
    username: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class OAuthExchangeRequest(BaseModel):
    code: str = Field(description="OAuth authorization code")
    redirect_uri: str = Field(
        description="Redirect URI used during OAuth authorization"
    )
    state: str = Field(
        description="OAuth state returned by /v1/auth/oauth/{provider}/start"
    )
    code_verifier: str = Field(
        description="PKCE code verifier returned by /v1/auth/oauth/{provider}/start"
    )


class OAuthStartResponse(BaseModel):
    authorize_url: str = Field(description="Provider authorization URL")
    state: str = Field(description="State to send back to /exchange")
    code_verifier: str = Field(description="PKCE verifier to store client-side")
    code_challenge: str = Field(description="PKCE challenge sent to provider")


class TokenData(BaseModel):
    email: str | None = None


# Subscription Schemas

class SubscriptionCreate(BaseModel):
    """Schema for creating a subscription via Stripe."""
    stripe_subscription_id: str = Field(description="Stripe subscription ID")
    stripe_customer_id: str = Field(description="Stripe customer ID")
    status: str = Field(description="Subscription status")
    plan_id: str = Field(default="premium_monthly")
    current_period_start: datetime
    current_period_end: datetime


class SubscriptionRead(BaseModel):
    """Schema for reading subscription info."""
    id: str
    user_id: str
    stripe_subscription_id: str
    status: str
    plan_id: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubscriptionStatusResponse(BaseModel):
    """Response showing user's subscription status."""
    is_subscriber: bool
    subscription: SubscriptionRead | None = None
    copies_remaining: int = Field(default=100, description="Copies remaining in billing period")


# Copy Tracking Schemas

class FlowCopyRequest(BaseModel):
    """Request to record a Flow copy."""
    flow_id: str = Field(description="ID of the Flow being copied")


class FlowCopyResponse(BaseModel):
    """Response after recording a copy."""
    id: str
    user_id: str
    flow_id: str
    copied_at: datetime
    copies_this_month: int = Field(description="Total copies by this user this month")
    copies_remaining: int = Field(description="Copies remaining this month")
    payout_earned: int = Field(description="Cents paid to creator for this copy (7 or 0)")

    class Config:
        from_attributes = True


class FlowCopyRead(BaseModel):
    """Schema for reading Flow copy events."""
    id: str
    user_id: str
    flow_id: str
    creator_id: str
    counted_for_payout: bool
    copied_at: datetime
    billing_month: datetime

    class Config:
        from_attributes = True


# Creator Payout Schemas

class CreatorPayoutRead(BaseModel):
    """Schema for reading creator payout info."""
    id: str
    creator_id: str
    billing_month: datetime
    copy_count: int
    amount_cents: int
    status: str
    stripe_transfer_id: str | None = None
    paid_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreatorEarningsResponse(BaseModel):
    """Response showing creator's earnings for a billing month."""
    billing_month: datetime
    copy_count: int
    amount_cents: int
    amount_dollars: float
    status: str
    paid_at: datetime | None = None


class CreatorAccountResponse(BaseModel):
    """Response showing creator account balance and settings."""
    user_id: str
    is_creator: bool
    account_balance_cents: int = Field(description="Cumulative balance on account")
    account_balance_dollars: float
    total_earnings_cents: int = Field(description="All-time earnings")
    total_earnings_dollars: float
    monthly_earnings: list[CreatorEarningsResponse]


# User Extensions

class UserReadWithBalance(UserRead):
    """Extended user info including subscription and creator balance."""
    is_creator: bool = False
    stripe_customer_id: str | None = None
    subscription: SubscriptionRead | None = None
    creator_account: CreatorAccountResponse | None = None

    class Config:
        from_attributes = True
