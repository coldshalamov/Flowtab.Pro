"""
CRUD operations for connection management.
"""

from typing import Optional

from sqlmodel import Session, select, col
from sqlalchemy import and_
from sqlalchemy.orm import selectinload

from models import Provider, AccountConnection, CredentialVaultItem, ManualOverride
from encryption import encryption_service
from schemas import ConnectionCreate, ConnectionRead, ProviderRead


def get_providers(session: Session, active_only: bool = True) -> list[Provider]:
    """
    Get all providers.

    Args:
        session: Database session
        active_only: If True, only return active providers

    Returns:
        List of providers
    """
    query = select(Provider)
    if active_only:
        query = query.where(Provider.is_active == True)

    return session.exec(query.order_by(col(Provider.display_name))).all()


def get_provider_by_id(session: Session, provider_id: str) -> Optional[Provider]:
    """
    Get a provider by ID.

    Args:
        session: Database session
        provider_id: Provider ID

    Returns:
        Provider or None
    """
    return session.exec(select(Provider).where(Provider.id == provider_id)).first()


def get_provider_by_slug(session: Session, slug: str) -> Optional[Provider]:
    """
    Get a provider by slug.

    Args:
        session: Database session
        slug: Provider slug

    Returns:
        Provider or None
    """
    return session.exec(select(Provider).where(Provider.slug == slug)).first()


def get_user_connections(
    session: Session, user_id: str, include_provider: bool = True
) -> list[AccountConnection]:
    """
    Get all connections for a user.

    Args:
        session: Database session
        user_id: User ID
        include_provider: If True, populate provider relationship

    Returns:
        List of connections
    """
    query = select(AccountConnection).where(AccountConnection.user_id == user_id)

    if include_provider:
        # Join with provider
        query = query.options(selectinload(AccountConnection.provider))

    return session.exec(query.order_by(AccountConnection.created_at.desc())).all()


def get_connection_by_id(
    session: Session, connection_id: str, user_id: str, include_provider: bool = True
) -> Optional[AccountConnection]:
    """
    Get a connection by ID, ensuring it belongs to the user.

    Args:
        session: Database session
        connection_id: Connection ID
        user_id: User ID (for authorization)
        include_provider: If True, populate provider relationship

    Returns:
        Connection or None
    """
    query = select(AccountConnection).where(
        and_(
            AccountConnection.id == connection_id, AccountConnection.user_id == user_id
        )
    )

    if include_provider:
        # Join with provider
        query = query.options(selectinload(AccountConnection.provider))

    return session.exec(query).first()


def create_connection(
    session: Session, user_id: str, connection_data: ConnectionCreate
) -> AccountConnection:
    """
    Create a new connection.

    Args:
        session: Database session
        user_id: User ID
        connection_data: Connection creation data

    Returns:
        Created connection

    Raises:
        ValueError: If provider not found or invalid connection type
    """
    # Validate provider exists
    provider = get_provider_by_id(session, connection_data.provider_id)
    if not provider:
        raise ValueError(f"Provider not found: {connection_data.provider_id}")

    # Validate connection type is supported by provider
    connection_type = connection_data.connection_type

    if connection_type == "api_key" and not provider.supports_api_key:
        raise ValueError(f"Provider does not support API key authentication")

    if connection_type == "oauth" and not provider.supports_oauth:
        raise ValueError(f"Provider does not support OAuth authentication")

    if connection_type == "manual" and not provider.supports_manual:
        raise ValueError(f"Provider does not support manual configuration")

    # Validate credentials are provided if needed
    if connection_type == "api_key" and not connection_data.credentials:
        raise ValueError("Credentials are required for API key connections")

    # Create the connection
    connection = AccountConnection(
        user_id=user_id,
        provider_id=provider.id,
        label=connection_data.label,
        connection_type=connection_type,
        status="active",
    )

    session.add(connection)
    session.flush()  # Get the connection ID

    # Encrypt and store credentials if provided
    if connection_data.credentials:
        for key_name, credential_value in connection_data.credentials.items():
            encrypted_data = encryption_service.encrypt(credential_value)

            vault_item = CredentialVaultItem(
                connection_id=connection.id,
                encrypted_data=encrypted_data,
                key_name=key_name,
            )
            session.add(vault_item)

    # Store manual config if provided
    if connection_data.manual_config:
        manual_override = ManualOverride(
            connection_id=connection.id, config=connection_data.manual_config
        )
        session.add(manual_override)

    session.commit()
    session.refresh(connection)

    return connection


def delete_connection(session: Session, connection_id: str, user_id: str) -> bool:
    """
    Delete a connection and its associated data.

    Args:
        session: Database session
        connection_id: Connection ID
        user_id: User ID (for authorization)

    Returns:
        True if deleted, False if not found
    """
    connection = get_connection_by_id(
        session, connection_id, user_id, include_provider=False
    )

    if not connection:
        return False

    # Delete associated credential vault items
    vault_items = session.exec(
        select(CredentialVaultItem).where(
            CredentialVaultItem.connection_id == connection_id
        )
    ).all()
    for item in vault_items:
        session.delete(item)

    # Delete associated manual overrides
    manual_overrides = session.exec(
        select(ManualOverride).where(ManualOverride.connection_id == connection_id)
    ).all()
    for override in manual_overrides:
        session.delete(override)

    # Delete the connection
    session.delete(connection)
    session.commit()

    return True


def get_connection_credentials(
    session: Session, connection_id: str, user_id: str
) -> dict[str, str]:
    """
    Get decrypted credentials for a connection.

    Args:
        session: Database session
        connection_id: Connection ID
        user_id: User ID (for authorization)

    Returns:
        Dictionary of decrypted credentials (key_name -> value)

    Raises:
        ValueError: If connection not found or not owned by user
    """
    # Verify connection exists and belongs to user
    connection = get_connection_by_id(
        session, connection_id, user_id, include_provider=False
    )
    if not connection:
        raise ValueError("Connection not found")

    # Get and decrypt credentials
    vault_items = session.exec(
        select(CredentialVaultItem).where(
            CredentialVaultItem.connection_id == connection_id
        )
    ).all()

    credentials = {}
    for item in vault_items:
        try:
            decrypted_value = encryption_service.decrypt(item.encrypted_data)
            credentials[item.key_name] = decrypted_value
        except Exception as e:
            raise ValueError(
                f"Failed to decrypt credential '{item.key_name}': {str(e)}"
            )

    return credentials


def get_manual_config(session: Session, connection_id: str, user_id: str) -> dict:
    """
    Get manual configuration for a connection.

    Args:
        session: Database session
        connection_id: Connection ID
        user_id: User ID (for authorization)

    Returns:
        Manual configuration dictionary

    Raises:
        ValueError: If connection not found or not owned by user
    """
    # Verify connection exists and belongs to user
    connection = get_connection_by_id(
        session, connection_id, user_id, include_provider=False
    )
    if not connection:
        raise ValueError("Connection not found")

    # Get manual override
    manual_override = session.exec(
        select(ManualOverride).where(ManualOverride.connection_id == connection_id)
    ).first()

    return manual_override.config if manual_override else {}


def update_connection_status(
    session: Session, connection_id: str, status: str, last_error: str | None = None
) -> AccountConnection:
    """
    Update the status of a connection.

    Args:
        session: Database session
        connection_id: Connection ID
        status: New status (active, inactive, error)
        last_error: Optional error message

    Returns:
        Updated connection
    """
    connection = session.exec(
        select(AccountConnection).where(AccountConnection.id == connection_id)
    ).first()

    if not connection:
        raise ValueError("Connection not found")

    connection.status = status
    if last_error:
        connection.last_error = last_error

    session.add(connection)
    session.commit()
    session.refresh(connection)

    return connection


def record_connection_usage(session: Session, connection_id: str) -> AccountConnection:
    """
    Record that a connection was used (update last_used_at timestamp).

    Args:
        session: Database session
        connection_id: Connection ID

    Returns:
        Updated connection
    """
    connection = session.exec(
        select(AccountConnection).where(AccountConnection.id == connection_id)
    ).first()

    if not connection:
        raise ValueError("Connection not found")

    from datetime import datetime

    connection.last_used_at = datetime.utcnow()
    connection.status = "active"
    connection.last_error = None

    session.add(connection)
    session.commit()
    session.refresh(connection)

    return connection
