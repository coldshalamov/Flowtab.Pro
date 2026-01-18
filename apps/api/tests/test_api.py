"""
API endpoint tests for the Flowtab.Pro backend.

This module contains tests for all API endpoints including:
- List prompts with pagination and filtering
- Get prompt by slug
- Get all tags
- Create new prompt (authenticated users)
"""

from apps.api.schemas import PromptCreate


def test_list_prompts_pagination(client, seeded_prompts):
    """
    Test listing prompts with pagination.

    Verifies that:
    - The API returns status 200
    - The correct number of items is returned based on pageSize
    - Pagination parameters are correctly reflected in the response
    - Total count reflects the number of seeded prompts
    """
    response = client.get("/v1/prompts?page=1&pageSize=10")

    assert response.status_code == 200
    data = response.json()

    assert len(data["items"]) == 10
    assert data["page"] == 1
    assert data["pageSize"] == 10
    assert data["total"] == 25


def test_filter_by_tag(client, db_session):
    """
    Test filtering prompts by tags.

    Verifies that:
    - The API returns status 200
    - Only prompts containing all specified tags are returned
    """
    from apps.api.models import Prompt

    # Seed prompts with specific tags
    prompt1 = Prompt(
        slug="git-workflow-prompt",
        title="Git Workflow Prompt",
        summary="A prompt for git workflow automation",
        difficulty="beginner",
        worksWith=["Chrome"],
        tags=["git", "workflow"],
        targetSites=["github.com"],
        promptText="Test prompt text",
        steps=["Step 1"],
    )
    prompt2 = Prompt(
        slug="git-only-prompt",
        title="Git Only Prompt",
        summary="A prompt for git only",
        difficulty="beginner",
        worksWith=["Chrome"],
        tags=["git"],
        targetSites=["github.com"],
        promptText="Test prompt text",
        steps=["Step 1"],
    )
    prompt3 = Prompt(
        slug="workflow-only-prompt",
        title="Workflow Only Prompt",
        summary="A prompt for workflow only",
        difficulty="beginner",
        worksWith=["Chrome"],
        tags=["workflow"],
        targetSites=["example.com"],
        promptText="Test prompt text",
        steps=["Step 1"],
    )

    db_session.add_all([prompt1, prompt2, prompt3])
    db_session.commit()

    response = client.get("/v1/prompts?tags=git,workflow")

    assert response.status_code == 200
    data = response.json()

    # Only prompt1 should be returned (has both git and workflow tags)
    assert len(data["items"]) == 1
    assert data["items"][0]["slug"] == "git-workflow-prompt"


def test_filter_by_difficulty(client, db_session):
    """
    Test filtering prompts by difficulty level.

    Verifies that:
    - The API returns status 200
    - Only prompts with the specified difficulty are returned
    """
    from apps.api.models import Prompt

    # Seed prompts with different difficulties
    prompt1 = Prompt(
        slug="beginner-prompt",
        title="Beginner Prompt",
        summary="A beginner prompt",
        difficulty="beginner",
        worksWith=["Chrome"],
        tags=["test"],
        targetSites=["example.com"],
        promptText="Test prompt text",
        steps=["Step 1"],
    )
    prompt2 = Prompt(
        slug="intermediate-prompt",
        title="Intermediate Prompt",
        summary="An intermediate prompt",
        difficulty="intermediate",
        worksWith=["Chrome"],
        tags=["test"],
        targetSites=["example.com"],
        promptText="Test prompt text",
        steps=["Step 1"],
    )
    prompt3 = Prompt(
        slug="advanced-prompt",
        title="Advanced Prompt",
        summary="An advanced prompt",
        difficulty="advanced",
        worksWith=["Chrome"],
        tags=["test"],
        targetSites=["example.com"],
        promptText="Test prompt text",
        steps=["Step 1"],
    )

    db_session.add_all([prompt1, prompt2, prompt3])
    db_session.commit()

    response = client.get("/v1/prompts?difficulty=intermediate")

    assert response.status_code == 200
    data = response.json()

    assert len(data["items"]) == 1
    assert data["items"][0]["difficulty"] == "intermediate"
    assert data["items"][0]["slug"] == "intermediate-prompt"


def test_get_prompt_by_slug(client, db_session):
    """
    Test getting a single prompt by slug.

    Verifies that:
    - The API returns status 200 when prompt exists
    - The returned prompt matches the expected data
    """
    from apps.api.models import Prompt

    # Seed a test prompt
    test_prompt = Prompt(
        slug="test-get-prompt",
        title="Test Get Prompt",
        summary="A test prompt for getting by slug",
        difficulty="beginner",
        worksWith=["Chrome"],
        tags=["test"],
        targetSites=["example.com"],
        promptText="Test prompt text",
        steps=["Step 1", "Step 2"],
        notes="Test notes",
    )

    db_session.add(test_prompt)
    db_session.commit()
    db_session.refresh(test_prompt)

    response = client.get("/v1/prompts/test-get-prompt")

    assert response.status_code == 200
    data = response.json()

    assert data["slug"] == "test-get-prompt"
    assert data["title"] == "Test Get Prompt"
    assert data["summary"] == "A test prompt for getting by slug"
    assert data["difficulty"] == "beginner"
    assert data["worksWith"] == ["Chrome"]
    assert data["tags"] == ["test"]
    assert data["targetSites"] == ["example.com"]
    assert data["promptText"] == "Test prompt text"
    assert data["steps"] == ["Step 1", "Step 2"]
    assert data["notes"] == "Test notes"
    assert "id" in data
    assert "createdAt" in data
    assert "updatedAt" in data


def test_get_prompt_by_slug_not_found(client, db_session):
    """
    Test getting a non-existent prompt by slug.

    Verifies that:
    - The API returns status 404
    - The error message contains "not found"
    """
    response = client.get("/v1/prompts/non-existent-slug")

    assert response.status_code == 404
    data = response.json()

    assert data["error"] == "Not found"
    assert "not found" in data["message"].lower()


def test_get_tags(client, db_session):
    """
    Test getting all available tags.

    Verifies that:
    - The API returns status 200
    - The response contains a list of strings
    - The list contains unique tags from seeded prompts
    """
    from apps.api.models import Prompt

    # Seed prompts with various tags
    prompt1 = Prompt(
        slug="tags-prompt-1",
        title="Tags Prompt 1",
        summary="Prompt with tags",
        difficulty="beginner",
        worksWith=["Chrome"],
        tags=["git", "workflow", "automation"],
        targetSites=["example.com"],
        promptText="Test prompt text",
        steps=["Step 1"],
    )
    prompt2 = Prompt(
        slug="tags-prompt-2",
        title="Tags Prompt 2",
        summary="Prompt with overlapping tags",
        difficulty="beginner",
        worksWith=["Chrome"],
        tags=["git", "testing"],
        targetSites=["example.com"],
        promptText="Test prompt text",
        steps=["Step 1"],
    )
    prompt3 = Prompt(
        slug="tags-prompt-3",
        title="Tags Prompt 3",
        summary="Prompt with different tags",
        difficulty="beginner",
        worksWith=["Chrome"],
        tags=["deployment", "ci-cd"],
        targetSites=["example.com"],
        promptText="Test prompt text",
        steps=["Step 1"],
    )

    db_session.add_all([prompt1, prompt2, prompt3])
    db_session.commit()

    response = client.get("/v1/tags")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data["items"], list)
    assert (
        len(data["items"]) == 6
    )  # git, workflow, automation, testing, deployment, ci-cd
    assert all(isinstance(tag, str) for tag in data["items"])
    assert "git" in data["items"]
    assert "workflow" in data["items"]
    assert "automation" in data["items"]
    assert "testing" in data["items"]
    assert "deployment" in data["items"]
    assert "ci-cd" in data["items"]


def test_create_prompt_authenticated_sets_author(
    client, db_session, auth_headers, registered_user
):
    """Test creating a new prompt as an authenticated user.

    Verifies that:
    - The API returns status 201
    - The returned prompt has the expected fields
    - The prompt is created in the database
    - author_id is set to the authenticated user's id
    """
    prompt_data = PromptCreate(
        slug="new-test-prompt",
        title="New Test Prompt",
        summary="A newly created test prompt",
        difficulty="intermediate",
        worksWith=["Chrome", "Firefox"],
        tags=["new", "test"],
        targetSites=["example.com"],
        promptText="This is a new test prompt",
        steps=["Step 1", "Step 2"],
        notes="New test notes",
    )

    response = client.post(
        "/v1/prompts",
        json=prompt_data.model_dump(),
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()

    assert data["slug"] == "new-test-prompt"
    assert data["title"] == "New Test Prompt"
    assert data["summary"] == "A newly created test prompt"
    assert data["difficulty"] == "intermediate"
    assert data["worksWith"] == ["Chrome", "Firefox"]
    assert data["tags"] == ["new", "test"]
    assert data["targetSites"] == ["example.com"]
    assert data["promptText"] == "This is a new test prompt"
    assert data["steps"] == ["Step 1", "Step 2"]
    assert data["notes"] == "New test notes"
    assert "id" in data
    assert "createdAt" in data
    assert "updatedAt" in data
    assert data["author_id"] == registered_user["id"]


def test_create_prompt_with_invalid_token(client, db_session):
    """Test creating a new prompt with an invalid bearer token."""
    prompt_data = PromptCreate(
        title="Unauthorized Prompt",
        summary="This prompt should not be created",
        difficulty="beginner",
        worksWith=["Chrome"],
        tags=["test"],
        targetSites=["example.com"],
        promptText="Test prompt text",
        steps=["Step 1"],
    )

    response = client.post(
        "/v1/prompts",
        json=prompt_data.model_dump(),
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    data = response.json()

    assert "detail" in data
    assert "validate" in data["detail"].lower()


def test_create_prompt_without_authentication(client, db_session):
    """Test creating a new prompt without authentication."""
    prompt_data = PromptCreate(
        title="No Admin Key Prompt",
        summary="This prompt should not be created",
        difficulty="beginner",
        worksWith=["Chrome"],
        tags=["test"],
        targetSites=["example.com"],
        promptText="Test prompt text",
        steps=["Step 1"],
    )

    response = client.post(
        "/v1/prompts",
        json=prompt_data.model_dump(),
    )

    assert response.status_code == 401
    data = response.json()

    assert "detail" in data
    assert "not authenticated" in data["detail"].lower()


def test_search_by_query(client, db_session):
    """
    Test searching prompts by text query.

    Verifies that:
    - The API returns status 200
    - Only prompts matching the search query are returned
    """
    from apps.api.models import Prompt

    # Seed prompts with different content
    prompt1 = Prompt(
        slug="search-test-1",
        title="Git Automation",
        summary="Automate git workflows",
        difficulty="beginner",
        worksWith=["Chrome"],
        tags=["git"],
        targetSites=["github.com"],
        promptText="This prompt helps with git automation",
        steps=["Step 1"],
    )
    prompt2 = Prompt(
        slug="search-test-2",
        title="Browser Testing",
        summary="Test browser applications",
        difficulty="beginner",
        worksWith=["Chrome"],
        tags=["testing"],
        targetSites=["example.com"],
        promptText="This prompt is for browser testing",
        steps=["Step 1"],
    )
    prompt3 = Prompt(
        slug="search-test-3",
        title="Deployment Scripts",
        summary="Deploy applications easily",
        difficulty="beginner",
        worksWith=["Chrome"],
        tags=["deployment"],
        targetSites=["example.com"],
        promptText="This prompt helps with deployment",
        steps=["Step 1"],
    )

    db_session.add_all([prompt1, prompt2, prompt3])
    db_session.commit()

    response = client.get("/v1/prompts?q=git")

    assert response.status_code == 200
    data = response.json()

    # Only prompt1 should match "git"
    assert len(data["items"]) == 1
    assert data["items"][0]["slug"] == "search-test-1"


def test_filter_by_workswith(client, db_session):
    """
    Test filtering prompts by compatible tools.

    Verifies that:
    - The API returns status 200
    - Only prompts compatible with specified tools are returned (OR logic)
    """
    from apps.api.models import Prompt

    # Seed prompts with different tools
    prompt1 = Prompt(
        slug="workswith-chrome",
        title="Chrome Only",
        summary="Works with Chrome",
        difficulty="beginner",
        worksWith=["Chrome"],
        tags=["test"],
        targetSites=["example.com"],
        promptText="Test prompt text",
        steps=["Step 1"],
    )
    prompt2 = Prompt(
        slug="workswith-firefox",
        title="Firefox Only",
        summary="Works with Firefox",
        difficulty="beginner",
        worksWith=["Firefox"],
        tags=["test"],
        targetSites=["example.com"],
        promptText="Test prompt text",
        steps=["Step 1"],
    )
    prompt3 = Prompt(
        slug="workswith-edge",
        title="Edge Only",
        summary="Works with Edge",
        difficulty="beginner",
        worksWith=["Edge"],
        tags=["test"],
        targetSites=["example.com"],
        promptText="Test prompt text",
        steps=["Step 1"],
    )

    db_session.add_all([prompt1, prompt2, prompt3])
    db_session.commit()

    response = client.get("/v1/prompts?worksWith=Chrome,Firefox")

    assert response.status_code == 200
    data = response.json()

    # Both Chrome and Firefox prompts should be returned (OR logic)
    assert len(data["items"]) == 2
    slugs = {item["slug"] for item in data["items"]}
    assert slugs == {"workswith-chrome", "workswith-firefox"}


def test_health_check(client):
    """
    Test the health check endpoint.

    Verifies that:
    - The API returns status 200
    - The response contains the expected status message
    """
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["message"] == "Flowtab.Pro API is running"
