"""Like system tests.

We support likes on flows (prompts) and comments.
"""


def _create_prompt(client, auth_headers) -> dict:
    payload = {
        "slug": None,
        "title": "Flow Thread",
        "summary": "A thread for discussion",

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


def _create_comment(client, auth_headers, prompt_slug: str) -> dict:
    resp = client.post(
        f"/v1/prompts/{prompt_slug}/comments",
        json={"body": "First!"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()


def test_like_prompt_requires_auth(client, db_session, auth_headers):
    prompt = _create_prompt(client, auth_headers)

    resp = client.put(f"/v1/prompts/{prompt['slug']}/like")
    assert resp.status_code == 401


def test_like_unlike_prompt_idempotent(client, db_session, auth_headers):
    prompt = _create_prompt(client, auth_headers)

    like1 = client.put(f"/v1/prompts/{prompt['slug']}/like", headers=auth_headers)
    assert like1.status_code == 200
    data1 = like1.json()
    assert data1["liked"] is True
    assert data1["likeCount"] == 1

    like2 = client.put(f"/v1/prompts/{prompt['slug']}/like", headers=auth_headers)
    assert like2.status_code == 200
    data2 = like2.json()
    assert data2["liked"] is True
    assert data2["likeCount"] == 1

    unlike1 = client.delete(f"/v1/prompts/{prompt['slug']}/like", headers=auth_headers)
    assert unlike1.status_code == 200
    data3 = unlike1.json()
    assert data3["liked"] is False
    assert data3["likeCount"] == 0

    unlike2 = client.delete(f"/v1/prompts/{prompt['slug']}/like", headers=auth_headers)
    assert unlike2.status_code == 200
    data4 = unlike2.json()
    assert data4["liked"] is False
    assert data4["likeCount"] == 0


def test_like_unlike_comment_idempotent(client, db_session, auth_headers):
    prompt = _create_prompt(client, auth_headers)
    comment = _create_comment(client, auth_headers, prompt_slug=prompt["slug"])

    like1 = client.put(f"/v1/comments/{comment['id']}/like", headers=auth_headers)
    assert like1.status_code == 200
    data1 = like1.json()
    assert data1["liked"] is True
    assert data1["likeCount"] == 1

    like2 = client.put(f"/v1/comments/{comment['id']}/like", headers=auth_headers)
    assert like2.status_code == 200
    assert like2.json()["likeCount"] == 1

    unlike1 = client.delete(f"/v1/comments/{comment['id']}/like", headers=auth_headers)
    assert unlike1.status_code == 200
    assert unlike1.json()["likeCount"] == 0

    unlike2 = client.delete(f"/v1/comments/{comment['id']}/like", headers=auth_headers)
    assert unlike2.status_code == 200
    assert unlike2.json()["likeCount"] == 0
