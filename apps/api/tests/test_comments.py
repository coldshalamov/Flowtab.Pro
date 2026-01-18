"""Comment/forum tests.

A prompt acts like a "thread"; comments are the forum replies.
"""


def _create_prompt(client, auth_headers) -> dict:
    payload = {
        "slug": None,
        "title": "Flow Thread",
        "summary": "A thread for discussion",
        "difficulty": "beginner",
        "worksWith": ["Chrome"],
        "tags": ["forum"],
        "targetSites": ["example.com"],
        "promptText": "Do the thing",
        "steps": ["One"],
        "notes": "",
    }
    resp = client.post("/v1/prompts", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    return resp.json()


def test_create_and_list_comments(client, db_session, auth_headers, registered_user):
    prompt = _create_prompt(client, auth_headers)

    create = client.post(
        f"/v1/prompts/{prompt['slug']}/comments",
        json={"body": "First!"},
        headers=auth_headers,
    )
    assert create.status_code == 201
    comment = create.json()

    assert comment["body"] == "First!"
    assert comment["author_id"] == registered_user["id"]
    assert comment["prompt_id"] == prompt["id"]
    assert "id" in comment
    assert "createdAt" in comment

    listing = client.get(f"/v1/prompts/{prompt['slug']}/comments")
    assert listing.status_code == 200
    items = listing.json()["items"]
    assert len(items) == 1
    assert items[0]["id"] == comment["id"]


def test_create_comment_requires_auth(client, db_session, auth_headers):
    prompt = _create_prompt(client, auth_headers)

    resp = client.post(
        f"/v1/prompts/{prompt['slug']}/comments",
        json={"body": "Nope"},
    )
    assert resp.status_code == 401


def test_delete_comment_author_only(client, db_session, auth_headers, registered_user):
    prompt = _create_prompt(client, auth_headers)
    create = client.post(
        f"/v1/prompts/{prompt['slug']}/comments",
        json={"body": "Hello"},
        headers=auth_headers,
    )
    assert create.status_code == 201
    comment = create.json()

    # Create a second user
    other_email = "other@example.com"
    other_password = "test-password-123"
    resp = client.post(
        "/v1/auth/register", json={"email": other_email, "password": other_password}
    )
    assert resp.status_code == 201

    other_token = client.post(
        "/v1/auth/token",
        data={"username": other_email, "password": other_password},
    )
    assert other_token.status_code == 200
    other_headers = {"Authorization": f"Bearer {other_token.json()['access_token']}"}

    forbidden = client.delete(f"/v1/comments/{comment['id']}", headers=other_headers)
    assert forbidden.status_code == 403

    ok = client.delete(f"/v1/comments/{comment['id']}", headers=auth_headers)
    assert ok.status_code == 204

    listing = client.get(f"/v1/prompts/{prompt['slug']}/comments")
    assert listing.status_code == 200
    assert listing.json()["items"] == []
