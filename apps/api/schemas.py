from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


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

    difficulty: Literal["beginner", "intermediate", "advanced"] = Field(
        description="Difficulty level of the prompt",
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

    steps: list[str] = Field(
        default_factory=list,
        description="Step-by-step instructions",
    )

    notes: str = Field(
        default="",
        description="Additional notes or warnings",
    )


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

    difficulty: Literal["beginner", "intermediate", "advanced"] = Field(
        description="Difficulty level of the prompt",
    )

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

    createdAt: datetime = Field(
        description="ISO 8601 timestamp when the prompt was created",
    )

    updatedAt: datetime = Field(
        description="ISO 8601 timestamp when the prompt was last updated",
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
    email: str = Field(description="User email address")


class UserCreate(UserBase):
    password: str = Field(description="User password", min_length=8)


class UserRead(UserBase):
    id: str
    is_active: bool
    is_superuser: bool
    createdAt: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
