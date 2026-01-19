"""OAuth endpoint tests for the Flowtab.Pro backend.

These tests validate the OAuth code exchange endpoints without making
any real network calls (httpx is monkeypatched).
"""

from sqlmodel import select


class _FakeHttpxResponse:
    def __init__(self, status_code: int, json_data: dict):
        self.status_code = status_code
        self._json_data = json_data
        self.text = str(json_data)

    def json(self) -> dict:
        return self._json_data


def test_oauth_exchange_creates_user_and_returns_token(client, db_session, monkeypatch):
    import httpx
    from apps.api.models import User, OAuthAccount

    def fake_post(url, *args, **kwargs):
        assert url == "https://oauth2.googleapis.com/token"
        return _FakeHttpxResponse(200, {"access_token": "google-access-token"})

    def fake_get(url, *args, **kwargs):
        assert url == "https://openidconnect.googleapis.com/v1/userinfo"
        return _FakeHttpxResponse(
            200,
            {
                "sub": "google-uid-123",
                "email": "new-google-user@example.com",
                "name": "New Google User",
            },
        )

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setattr(httpx, "get", fake_get)

    start = client.post(
        "/v1/auth/oauth/google/start",
        params={"redirect_uri": "http://localhost/callback"},
    )
    assert start.status_code == 200
    start_data = start.json()

    response = client.post(
        "/v1/auth/oauth/google/exchange",
        json={
            "code": "dummy-code",
            "redirect_uri": "http://localhost/callback",
            "state": start_data["state"],
            "code_verifier": start_data["code_verifier"],
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["token_type"] == "bearer"
    assert data["access_token"]

    users = db_session.exec(select(User)).all()
    assert len(users) == 1
    assert users[0].email == "new-google-user@example.com"

    accounts = db_session.exec(select(OAuthAccount)).all()
    assert len(accounts) == 1
    assert accounts[0].provider == "google"
    assert accounts[0].provider_user_id == "google-uid-123"
    assert accounts[0].user_id == users[0].id


def test_oauth_exchange_existing_email_requires_linking(
    client, db_session, monkeypatch
):
    """If a user already exists with the same email, we don't auto-link.

    This prevents account-takeover where someone registers an email/password
    account for a victim's email, then the victim later uses OAuth.
    """

    import httpx
    from apps.api.auth import get_password_hash
    from apps.api.models import User, OAuthAccount

    existing = User(
        email="existing@example.com",
        username="existinguser",
        hashed_password=get_password_hash("test-password-123"),
        is_active=True,
        is_superuser=False,
    )
    db_session.add(existing)
    db_session.commit()
    db_session.refresh(existing)

    def fake_post(url, *args, **kwargs):
        return _FakeHttpxResponse(200, {"access_token": "google-access-token"})

    def fake_get(url, *args, **kwargs):
        return _FakeHttpxResponse(
            200,
            {
                "sub": "google-uid-999",
                "email": "existing@example.com",
            },
        )

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setattr(httpx, "get", fake_get)

    start = client.post(
        "/v1/auth/oauth/google/start",
        params={"redirect_uri": "http://localhost/callback"},
    )
    assert start.status_code == 200
    start_data = start.json()

    response = client.post(
        "/v1/auth/oauth/google/exchange",
        json={
            "code": "dummy-code",
            "redirect_uri": "http://localhost/callback",
            "state": start_data["state"],
            "code_verifier": start_data["code_verifier"],
        },
    )

    assert response.status_code == 409

    # No OAuth account auto-linked
    accounts = db_session.exec(select(OAuthAccount)).all()
    assert accounts == []


def test_oauth_link_existing_user(
    client, db_session, auth_headers, registered_user, monkeypatch
):
    """Authenticated users can explicitly link an OAuth provider."""

    import httpx
    from apps.api.models import OAuthAccount

    def fake_post(url, *args, **kwargs):
        assert url == "https://oauth2.googleapis.com/token"
        return _FakeHttpxResponse(200, {"access_token": "google-access-token"})

    def fake_get(url, *args, **kwargs):
        assert url == "https://openidconnect.googleapis.com/v1/userinfo"
        return _FakeHttpxResponse(
            200,
            {
                "sub": "google-uid-555",
                "email": registered_user["email"],
            },
        )

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setattr(httpx, "get", fake_get)

    start = client.post(
        "/v1/auth/oauth/google/start",
        params={"redirect_uri": "http://localhost/callback"},
    )
    assert start.status_code == 200
    start_data = start.json()

    response = client.post(
        "/v1/auth/oauth/google/link",
        json={
            "code": "dummy-code",
            "redirect_uri": "http://localhost/callback",
            "state": start_data["state"],
            "code_verifier": start_data["code_verifier"],
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    accounts = db_session.exec(select(OAuthAccount)).all()
    assert len(accounts) == 1
    assert accounts[0].provider == "google"
    assert accounts[0].provider_user_id == "google-uid-555"
    assert accounts[0].user_id == registered_user["id"]
