"""
API routes for connection management.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from db import get_session
from auth import get_current_user
from models import User, Provider
from schemas import (
    ProviderRead,
    ConnectionCreate,
    ConnectionRead,
    ConnectionListResponse,
    ErrorResponse,
)
from connections_crud import (
    get_providers,
    get_user_connections,
    get_connection_by_id,
    create_connection,
    delete_connection,
    update_connection_status,
)

router = APIRouter(prefix="/v1/connections", tags=["connections"])


# Provider endpoints


@router.get("/providers", response_model=list[ProviderRead])
def list_providers(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
):
    """
    List all available AI providers.

    Requires authentication.
    """
    providers = get_providers(session, active_only=True)
    return providers


# Connection endpoints


@router.get("", response_model=ConnectionListResponse)
def list_connections(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
):
    """
    List all connections for the authenticated user.

    Requires authentication. Returns connections with provider information
    but never includes decrypted credentials.
    """
    connections = get_user_connections(session, current_user.id, include_provider=True)

    # Convert to response schemas
    connection_reads = []
    for conn in connections:
        connection_dict = {
            "id": conn.id,
            "user_id": conn.user_id,
            "provider_id": conn.provider_id,
            "label": conn.label,
            "connection_type": conn.connection_type,
            "status": conn.status,
            "last_used_at": conn.last_used_at,
            "last_error": conn.last_error,
            "created_at": conn.created_at,
            "updated_at": conn.updated_at,
            "provider": None,
        }

        # Add provider info if available
        if hasattr(conn, "provider") and conn.provider:
            provider = conn.provider
            connection_dict["provider"] = ProviderRead(
                id=provider.id,
                name=provider.name,
                slug=provider.slug,
                display_name=provider.display_name,
                description=provider.description,
                api_endpoint=provider.api_endpoint,
                auth_type=provider.auth_type,
                supports_api_key=provider.supports_api_key,
                supports_oauth=provider.supports_oauth,
                supports_manual=provider.supports_manual,
                rate_limit_per_minute=provider.rate_limit_per_minute,
                rate_limit_per_hour=provider.rate_limit_per_hour,
                documentation_url=provider.documentation_url,
                is_active=provider.is_active,
            )

        connection_reads.append(ConnectionRead(**connection_dict))

    return ConnectionListResponse(items=connection_reads)


@router.post("", response_model=ConnectionRead, status_code=status.HTTP_201_CREATED)
def create_connection_route(
    connection_data: ConnectionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
):
    """
    Create a new connection to an AI provider.

    Requires authentication. Credentials are encrypted before storage.
    """
    try:
        connection = create_connection(session, current_user.id, connection_data)

        # Get provider info for response
        provider = get_providers.__globals__["get_provider_by_id"](
            session, connection.provider_id
        )

        connection_dict = {
            "id": connection.id,
            "user_id": connection.user_id,
            "provider_id": connection.provider_id,
            "label": connection.label,
            "connection_type": connection.connection_type,
            "status": connection.status,
            "last_used_at": connection.last_used_at,
            "last_error": connection.last_error,
            "created_at": connection.created_at,
            "updated_at": connection.updated_at,
            "provider": ProviderRead.model_validate(provider) if provider else None,
        }

        return ConnectionRead(**connection_dict)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create connection: {str(e)}",
        )


@router.delete("/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_connection_route(
    connection_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
):
    """
    Delete a connection.

    Requires authentication. Users can only delete their own connections.
    All associated credentials and configurations are also deleted.
    """
    success = delete_connection(session, connection_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    return None


@router.get("/{connection_id}", response_model=ConnectionRead)
def get_connection_route(
    connection_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
):
    """
    Get a specific connection by ID.

    Requires authentication. Users can only view their own connections.
    Returns connection details without decrypted credentials.
    """
    connection = get_connection_by_id(
        session, connection_id, current_user.id, include_provider=True
    )

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    # Get provider info for response
    provider = get_providers.__globals__["get_provider_by_id"](
        session, connection.provider_id
    )

    connection_dict = {
        "id": connection.id,
        "user_id": connection.user_id,
        "provider_id": connection.provider_id,
        "label": connection.label,
        "connection_type": connection.connection_type,
        "status": connection.status,
        "last_used_at": connection.last_used_at,
        "last_error": connection.last_error,
        "created_at": connection.created_at,
        "updated_at": connection.updated_at,
        "provider": ProviderRead.model_validate(provider) if provider else None,
    }

    return ConnectionRead(**connection_dict)
