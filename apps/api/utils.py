"""
Utility functions for the Flowtab.Pro backend API.

This module provides helper functions for formatting responses and handling errors.
"""

from typing import Any
from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError


def error_response(
    error: str,
    message: str,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
) -> JSONResponse:
    """
    Create a standardized error response in the format specified in the OpenAPI contract.

    Args:
        error: Error type or category (e.g., "Not found", "Unauthorized")
        message: Human-readable error message
        status_code: HTTP status code to return

    Returns:
        JSONResponse with error format: {"error": "...", "message": "..."}
    """
    return JSONResponse(
        status_code=status_code,
        content={"error": error, "message": message},
    )


def validation_error_response(
    message: str = "Request body validation failed",
    details: list[dict[str, Any]] | None = None,
) -> JSONResponse:
    """
    Create a validation error response with field-level details.

    Args:
        message: General error message
        details: List of validation error details with 'field' and 'message' keys

    Returns:
        JSONResponse with validation error format: {"error": "Validation error", "message": "...", "details": [...]}
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "message": message,
            "details": details or [],
        },
    )


def format_pydantic_validation_error(exc: PydanticValidationError) -> list[dict[str, Any]]:
    """
    Format Pydantic ValidationError into the format expected by the API.

    Args:
        exc: Pydantic ValidationError exception

    Returns:
        List of error details with 'field' and 'message' keys
    """
    details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        details.append(
            {
                "field": field,
                "message": error["msg"],
            }
        )
    return details
