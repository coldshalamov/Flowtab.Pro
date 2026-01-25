"""
Integration tests for connection management API.
"""

import os
import pytest

from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, select

os.environ["TESTING"] = "true"

from main import app
from models import (
    User,
    Provider,
    AccountConnection,
    CredentialVaultItem,
    ManualOverride,
)
from db import set_test_engine
from encryption import encryption_service


@pytest.fixture
def test_db():
    """Create a test database."""
    engine = create_engine("sqlite:///:memory:")
    set_test_engine(engine)

    # Create tables
    from models import SQLModel

    SQLModel.metadata.create_all(engine)

    # Seed providers
    session = Session(engine)
    providers = [
        Provider(
            name="zai",
            slug="zai",
            display_name="Z.ai",
            description="Test provider",
            api_endpoint="https://api.example.com",
            auth_type="api_key",
            supports_api_key=True,
            supports_oauth=False,
            supports_manual=True,
            rate_limit_per_minute=100,
        ),
        Provider(
            name="github_copilot",
            slug="github-copilot",
            display_name="GitHub Copilot",
            description="OAuth test provider",
            auth_type="oauth",
            supports_api_key=False,
            supports_oauth=True,
            supports_manual=True,
        ),
    ]
    for provider in providers:
        session.add(provider)
    session.commit()

    yield session

    session.close()


@pytest.fixture
def test_user(test_db: Session):
    """Create a test user."""
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash("testpassword")

    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hashed_password,
        is_active=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    return user


@pytest.fixture
def auth_token(test_user: User, client: TestClient):
    """Get authentication token for test user."""
    response = client.post(
        "/v1/auth/token",
        data={"username": "testuser", "password": "testpassword"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def authenticated_client(client: TestClient, auth_token: str):
    """Create authenticated test client."""
    client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return client


class TestProvidersAPI:
    """Test cases for providers API."""

    def test_list_providers(self, authenticated_client: TestClient):
        """Test listing all providers."""
        response = authenticated_client.get("/v1/connections/providers")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        assert any(p["slug"] == "zai" for p in data)
        assert any(p["slug"] == "github-copilot" for p in data)

    def test_provider_has_required_fields(self, authenticated_client: TestClient):
        """Test that provider response has all required fields."""
        response = authenticated_client.get("/v1/connections/providers")
        data = response.json()

        provider = data[0]

        assert "id" in provider
        assert "name" in provider
        assert "slug" in provider
        assert "display_name" in provider
        assert "description" in provider
        assert "auth_type" in provider
        assert "supports_api_key" in provider
        assert "supports_oauth" in provider
        assert "supports_manual" in provider

    def test_providers_requires_auth(self, client: TestClient):
        """Test that providers endpoint requires authentication."""
        response = client.get("/v1/connections/providers")

        assert response.status_code == 401


class TestConnectionsAPI:
    """Test cases for connections API."""

    def test_list_connections_empty(self, authenticated_client: TestClient):
        """Test listing connections when user has none."""
        response = authenticated_client.get("/v1/connections")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["items"] == []

    def test_create_connection_with_api_key(
        self, authenticated_client: TestClient, test_db: Session
    ):
        """Test creating a connection with API key."""
        # Get provider ID
        provider = test_db.exec(select(Provider).where(Provider.slug == "zai")).first()

        connection_data = {
            "provider_id": provider.id,
            "label": "My Z.ai Connection",
            "connection_type": "api_key",
            "credentials": {"api_key": "sk-test1234567890"},
        }

        response = authenticated_client.post("/v1/connections", json=connection_data)

        assert response.status_code == 201
        data = response.json()
        assert data["label"] == "My Z.ai Connection"
        assert data["connection_type"] == "api_key"
        assert data["status"] == "active"
        assert "credentials" not in data  # Credentials should never be returned

    def test_create_connection_with_manual_config(
        self, authenticated_client: TestClient, test_db: Session
    ):
        """Test creating a connection with manual config."""
        provider = test_db.exec(select(Provider).where(Provider.slug == "zai")).first()

        connection_data = {
            "provider_id": provider.id,
            "label": "Manual Config",
            "connection_type": "manual",
            "manual_config": {"model": "gpt-4", "temperature": 0.7},
        }

        response = authenticated_client.post("/v1/connections", json=connection_data)

        assert response.status_code == 201
        data = response.json()
        assert data["label"] == "Manual Config"
        assert data["connection_type"] == "manual"

    def test_create_connection_without_credentials(
        self, authenticated_client: TestClient, test_db: Session
    ):
        """Test that creating API key connection without credentials fails."""
        provider = test_db.exec(select(Provider).where(Provider.slug == "zai")).first()

        connection_data = {
            "provider_id": provider.id,
            "label": "Invalid Connection",
            "connection_type": "api_key",
            "credentials": None,
        }

        response = authenticated_client.post("/v1/connections", json=connection_data)

        assert response.status_code == 400

    def test_create_connection_invalid_provider(self, authenticated_client: TestClient):
        """Test that creating connection with invalid provider fails."""
        connection_data = {
            "provider_id": "invalid-provider-id",
            "label": "Test",
            "connection_type": "api_key",
        }

        response = authenticated_client.post("/v1/connections", json=connection_data)

        assert response.status_code == 400

    def test_list_connections_with_data(
        self, authenticated_client: TestClient, test_db: Session
    ):
        """Test listing connections after creating one."""
        provider = test_db.exec(select(Provider).where(Provider.slug == "zai")).first()

        connection_data = {
            "provider_id": provider.id,
            "label": "Test Connection",
            "connection_type": "api_key",
            "credentials": {"api_key": "sk-test"},
        }

        authenticated_client.post("/v1/connections", json=connection_data)

        response = authenticated_client.get("/v1/connections")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["label"] == "Test Connection"
        assert data["items"][0]["provider"]["slug"] == "zai"

    def test_get_connection_by_id(
        self, authenticated_client: TestClient, test_db: Session
    ):
        """Test getting a specific connection."""
        provider = test_db.exec(select(Provider).where(Provider.slug == "zai")).first()

        connection_data = {
            "provider_id": provider.id,
            "label": "Test Connection",
            "connection_type": "api_key",
            "credentials": {"api_key": "sk-test"},
        }

        create_response = authenticated_client.post(
            "/v1/connections", json=connection_data
        )
        connection_id = create_response.json()["id"]

        response = authenticated_client.get(f"/v1/connections/{connection_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == connection_id
        assert data["label"] == "Test Connection"
        assert "credentials" not in data

    def test_get_connection_not_found(self, authenticated_client: TestClient):
        """Test getting non-existent connection."""
        response = authenticated_client.get("/v1/connections/non-existent-id")

        assert response.status_code == 404

    def test_delete_connection(
        self, authenticated_client: TestClient, test_db: Session
    ):
        """Test deleting a connection."""
        provider = test_db.exec(select(Provider).where(Provider.slug == "zai")).first()

        connection_data = {
            "provider_id": provider.id,
            "label": "To Delete",
            "connection_type": "api_key",
            "credentials": {"api_key": "sk-test"},
        }

        create_response = authenticated_client.post(
            "/v1/connections", json=connection_data
        )
        connection_id = create_response.json()["id"]

        response = authenticated_client.delete(f"/v1/connections/{connection_id}")

        assert response.status_code == 204

        # Verify it's deleted
        get_response = authenticated_client.get(f"/v1/connections/{connection_id}")
        assert get_response.status_code == 404

    def test_delete_connection_not_found(self, authenticated_client: TestClient):
        """Test deleting non-existent connection."""
        response = authenticated_client.delete("/v1/connections/non-existent-id")

        assert response.status_code == 404

    def test_connections_requires_auth(self, client: TestClient):
        """Test that connection endpoints require authentication."""
        # Test list
        response = client.get("/v1/connections")
        assert response.status_code == 401

        # Test create
        response = client.post("/v1/connections", json={})
        assert response.status_code == 401

        # Test delete
        response = client.delete("/v1/connections/some-id")
        assert response.status_code == 401


class TestCredentialEncryption:
    """Test that credentials are properly encrypted in the database."""

    def test_credentials_encrypted_in_db(
        self, test_db: Session, authenticated_client: TestClient
    ):
        """Verify credentials are encrypted in the database."""
        provider = test_db.exec(select(Provider).where(Provider.slug == "zai")).first()

        connection_data = {
            "provider_id": provider.id,
            "label": "Encrypted Test",
            "connection_type": "api_key",
            "credentials": {"api_key": "sk-secret-key-12345"},
        }

        response = authenticated_client.post("/v1/connections", json=connection_data)
        connection_id = response.json()["id"]

        # Query database directly
        vault_items = test_db.exec(
            select(CredentialVaultItem).where(
                CredentialVaultItem.connection_id == connection_id
            )
        ).all()

        assert len(vault_items) == 1
        vault_item = vault_items[0]

        # Verify encrypted data is not plaintext
        assert vault_item.encrypted_data != "sk-secret-key-12345"
        assert (
            ":" in vault_item.encrypted_data
        )  # Should have iv:auth_tag:content format

    def test_credentials_can_be_decrypted(
        self, test_db: Session, authenticated_client: TestClient
    ):
        """Verify encrypted credentials can be decrypted."""
        provider = test_db.exec(select(Provider).where(Provider.slug == "zai")).first()

        original_key = "sk-test-key-67890"
        connection_data = {
            "provider_id": provider.id,
            "label": "Decrypt Test",
            "connection_type": "api_key",
            "credentials": {"api_key": original_key},
        }

        response = authenticated_client.post("/v1/connections", json=connection_data)
        connection_id = response.json()["id"]

        # Query database and decrypt
        vault_item = test_db.exec(
            select(CredentialVaultItem).where(
                CredentialVaultItem.connection_id == connection_id
            )
        ).first()

        decrypted = encryption_service.decrypt(vault_item.encrypted_data)

        assert decrypted == original_key
