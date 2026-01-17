import os
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from apps.api.settings import settings
from apps.api.db import init_db
from apps.api.router import router
from apps.api.utils import validation_error_response, format_pydantic_validation_error

app = FastAPI(
    title="Flowtab.Pro API",
    description="API for Flowtab.Pro - A library of automated browser prompt recipes",
    version="0.1.0",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle request validation errors and return formatted error response.

    This exception handler catches validation errors that occur during
    request body validation (before the endpoint function is called).
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
    return validation_error_response(
        message="Request body validation failed",
        details=details,
    )


@app.on_event("startup")
def on_startup() -> None:
    """Initialize the database on startup."""
    # Skip database initialization during tests
    if os.getenv("TESTING") != "true":
        init_db()


@app.get("/")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "message": "Flowtab.Pro API is running"}


# Include API router
app.include_router(router)
