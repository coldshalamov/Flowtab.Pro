"""
API router for the Flowtab.Pro backend API.

This module defines all API endpoints for the prompts API.
"""

import logging
from typing import Literal

from fastapi import APIRouter, Depends, Query, Header, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError
from sqlmodel import Session

from apps.api.schemas import (
    PromptCreate,
    PromptRead,
    PromptListResponse,
    TagsResponse,
)
from apps.api.crud import (
    get_prompt_by_slug,
    get_prompts,
    get_all_tags,
    create_prompt,
)
from apps.api.settings import settings
from apps.api.db import get_session
from apps.api.utils import (
    error_response,
    validation_error_response,
    format_pydantic_validation_error,
)

logger = logging.getLogger(__name__)

# Create API router with prefix and tags
router = APIRouter(prefix="/v1", tags=["prompts"])


@router.get("/prompts", response_model=PromptListResponse, status_code=status.HTTP_200_OK)
def list_prompts(
    q: str | None = Query(default=None, description="Search query for text search"),
    tags: str | None = Query(default=None, description="Comma-separated list of tags to filter by"),
    difficulty: Literal["beginner", "intermediate", "advanced"] | None = Query(
        default=None, description="Difficulty level to filter by"
    ),
    worksWith: str | None = Query(
        default=None, description="Comma-separated list of tools to filter by"
    ),
    page: int = Query(default=1, ge=1, description="Page number"),
    pageSize: int = Query(default=20, ge=1, le=100, description="Number of items per page"),
    session: Session = Depends(get_session),
) -> PromptListResponse | JSONResponse:
    """
    List all prompts with optional filtering, search, and pagination.

    Query parameters:
    - q: Search query for text search across title, summary, and promptText
    - tags: Comma-separated list of tags to filter by (AND logic)
    - difficulty: Difficulty level to filter by (beginner, intermediate, advanced)
    - worksWith: Comma-separated list of tools to filter by (OR logic)
    - page: Page number (default: 1)
    - pageSize: Number of items per page (default: 20, max: 100)
    """
    try:
        # Parse comma-separated parameters into lists
        tags_list = tags.split(",") if tags else None
        works_with_list = worksWith.split(",") if worksWith else None

        # Calculate skip for pagination
        skip = (page - 1) * pageSize

        # Call get_prompts with filters
        prompts, total = get_prompts(
            session=session,
            skip=skip,
            limit=pageSize,
            q=q,
            tags=tags_list,
            difficulty=difficulty,
            worksWith=works_with_list,
        )

        # Return PromptListResponse
        return PromptListResponse(
            items=prompts,
            page=page,
            pageSize=pageSize,
            total=total,
        )

    except Exception:
        logger.exception("Unhandled error in GET /v1/prompts")
        return error_response(
            error="Internal server error",
            message="An unexpected error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/prompts/{slug}", response_model=PromptRead, status_code=status.HTTP_200_OK)
def get_prompt(slug: str, session: Session = Depends(get_session)) -> PromptRead | JSONResponse:
    """
    Get a single prompt by slug.

    Path parameter:
    - slug: URL-friendly unique identifier of the prompt

    Returns the prompt if found, raises 404 if not found.
    """
    try:
        prompt = get_prompt_by_slug(session=session, slug=slug)

        if prompt is None:
            return error_response(
                error="Not found",
                message=f"Prompt with slug '{slug}' not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return prompt

    except Exception:
        logger.exception("Unhandled error in GET /v1/prompts/{slug} (slug=%s)", slug)
        return error_response(
            error="Internal server error",
            message="An unexpected error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/tags", response_model=TagsResponse, status_code=status.HTTP_200_OK)
def list_tags(session: Session = Depends(get_session)) -> TagsResponse | JSONResponse:
    """
    Get all available tags.

    Returns a list of all unique tags across all prompts.
    """
    try:
        tags = get_all_tags(session=session)
        return TagsResponse(items=tags)

    except Exception:
        logger.exception("Unhandled error in GET /v1/tags")
        return error_response(
            error="Internal server error",
            message="An unexpected error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/prompts", response_model=PromptRead, status_code=status.HTTP_201_CREATED)
def create_new_prompt(
    prompt: PromptCreate,
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
    session: Session = Depends(get_session),
) -> PromptRead | JSONResponse:
    """
    Create a new prompt.

    Request body: PromptCreate schema with all required fields
    Header: X-Admin-Key - Admin authentication key

    Admin authentication is required via the X-Admin-Key header.
    """
    if not settings.admin_key:
        return error_response(
            error="Service unavailable",
            message="Admin submissions are disabled (missing ADMIN_KEY).",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    # Verify admin key
    if x_admin_key != settings.admin_key:
        return error_response(
            error="Unauthorized",
            message="Invalid or missing X-Admin-Key header",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        new_prompt = create_prompt(session=session, prompt_create=prompt)
        return new_prompt

    except PydanticValidationError as e:
        return validation_error_response(
            message="Request body validation failed",
            details=format_pydantic_validation_error(e),
        )
    except Exception:
        logger.exception("Unhandled error in POST /v1/prompts")
        return error_response(
            error="Internal server error",
            message="An unexpected error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
