"""
CRUD function tests for the Flowtab.Pro backend.

This module contains tests for the CRUD functions in crud.py:
- get_prompt_by_slug
- get_prompts
- get_all_tags
- create_prompt
- slugify_title
"""

from apps.api.crud import (
    get_prompt_by_slug,
    get_prompts,
    get_all_tags,
    create_prompt,
    slugify_title,
)
from apps.api.schemas import PromptCreate


def test_get_prompt_by_slug_found(db_session):
    """
    Test getting a prompt by slug when it exists.
    
    Verifies that:
    - The function returns the correct prompt
    - All fields are populated correctly
    """
    from apps.api.models import Prompt
    
    # Create a test prompt
    test_prompt = Prompt(
        slug="test-slug",
        title="Test Title",
        summary="Test Summary",
        difficulty="beginner",
        worksWith=["Chrome"],
        tags=["test"],
        targetSites=["example.com"],
        promptText="Test prompt text",
        steps=["Step 1"],
    )
    
    db_session.add(test_prompt)
    db_session.commit()
    db_session.refresh(test_prompt)
    
    # Get the prompt by slug
    result = get_prompt_by_slug(db_session, "test-slug")
    
    assert result is not None
    assert result.slug == "test-slug"
    assert result.title == "Test Title"
    assert result.summary == "Test Summary"
    assert result.difficulty == "beginner"


def test_get_prompt_by_slug_not_found(db_session):
    """
    Test getting a prompt by slug when it doesn't exist.
    
    Verifies that:
    - The function returns None
    """
    result = get_prompt_by_slug(db_session, "non-existent-slug")
    
    assert result is None


def test_get_prompts_all(db_session):
    """
    Test getting all prompts without filters.
    
    Verifies that:
    - The function returns all prompts
    - The total count is correct
    """
    from apps.api.models import Prompt
    
    # Create test prompts
    for i in range(5):
        prompt = Prompt(
            slug=f"test-prompt-{i}",
            title=f"Test Prompt {i}",
            summary=f"Summary {i}",
            difficulty="beginner",
            worksWith=["Chrome"],
            tags=["test"],
            targetSites=["example.com"],
            promptText=f"Prompt text {i}",
            steps=["Step 1"],
        )
        db_session.add(prompt)
    
    db_session.commit()
    
    # Get all prompts
    prompts, total = get_prompts(db_session)
    
    assert len(prompts) == 5
    assert total == 5


def test_get_prompts_pagination(db_session):
    """
    Test getting prompts with pagination.
    
    Verifies that:
    - The function returns the correct number of prompts based on skip/limit
    - The total count is unaffected by pagination
    """
    from apps.api.models import Prompt
    
    # Create 10 test prompts
    for i in range(10):
        prompt = Prompt(
            slug=f"test-prompt-{i}",
            title=f"Test Prompt {i}",
            summary=f"Summary {i}",
            difficulty="beginner",
            worksWith=["Chrome"],
            tags=["test"],
            targetSites=["example.com"],
            promptText=f"Prompt text {i}",
            steps=["Step 1"],
        )
        db_session.add(prompt)
    
    db_session.commit()
    
    # Get first page
    prompts, total = get_prompts(db_session, skip=0, limit=5)
    
    assert len(prompts) == 5
    assert total == 10
    
    # Get second page
    prompts, total = get_prompts(db_session, skip=5, limit=5)
    
    assert len(prompts) == 5
    assert total == 10


def test_get_prompts_filter_by_difficulty(db_session):
    """
    Test getting prompts filtered by difficulty.
    
    Verifies that:
    - Only prompts with the specified difficulty are returned
    - The total count reflects the filtered results
    """
    from apps.api.models import Prompt
    
    # Create prompts with different difficulties
    difficulties = ["beginner", "intermediate", "advanced"]
    for i, difficulty in enumerate(difficulties):
        prompt = Prompt(
            slug=f"test-prompt-{difficulty}",
            title=f"Test Prompt {difficulty}",
            summary=f"Summary {difficulty}",
            difficulty=difficulty,
            worksWith=["Chrome"],
            tags=["test"],
            targetSites=["example.com"],
            promptText=f"Prompt text {difficulty}",
            steps=["Step 1"],
        )
        db_session.add(prompt)
    
    db_session.commit()
    
    # Filter by intermediate difficulty
    prompts, total = get_prompts(db_session, difficulty="intermediate")
    
    assert len(prompts) == 1
    assert total == 1
    assert prompts[0].difficulty == "intermediate"


def test_get_prompts_filter_by_tags(db_session):
    """
    Test getting prompts filtered by tags (AND logic).
    
    Verifies that:
    - Only prompts containing ALL specified tags are returned
    """
    from apps.api.models import Prompt
    
    # Create prompts with different tag combinations
    prompt1 = Prompt(
        slug="tags-prompt-1",
        title="Tags Prompt 1",
        summary="Prompt with git and workflow",
        difficulty="beginner",
        worksWith=["Chrome"],
        tags=["git", "workflow"],
        targetSites=["example.com"],
        promptText="Test prompt text",
        steps=["Step 1"],
    )
    prompt2 = Prompt(
        slug="tags-prompt-2",
        title="Tags Prompt 2",
        summary="Prompt with git only",
        difficulty="beginner",
        worksWith=["Chrome"],
        tags=["git"],
        targetSites=["example.com"],
        promptText="Test prompt text",
        steps=["Step 1"],
    )
    prompt3 = Prompt(
        slug="tags-prompt-3",
        title="Tags Prompt 3",
        summary="Prompt with workflow only",
        difficulty="beginner",
        worksWith=["Chrome"],
        tags=["workflow"],
        targetSites=["example.com"],
        promptText="Test prompt text",
        steps=["Step 1"],
    )
    
    db_session.add_all([prompt1, prompt2, prompt3])
    db_session.commit()
    
    # Filter by both git and workflow tags (AND logic)
    prompts, total = get_prompts(db_session, tags=["git", "workflow"])
    
    assert len(prompts) == 1
    assert total == 1
    assert prompts[0].slug == "tags-prompt-1"


def test_get_prompts_search_by_query(db_session):
    """
    Test getting prompts with text search.
    
    Verifies that:
    - Only prompts matching the search query are returned
    - Search works across title, summary, and promptText
    """
    from apps.api.models import Prompt
    
    # Create prompts with different content
    prompt1 = Prompt(
        slug="search-prompt-1",
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
        slug="search-prompt-2",
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
        slug="search-prompt-3",
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
    
    # Search for "git"
    prompts, total = get_prompts(db_session, q="git")
    
    assert len(prompts) == 1
    assert total == 1
    assert prompts[0].slug == "search-prompt-1"


def test_get_all_tags(db_session):
    """
    Test getting all unique tags from prompts.
    
    Verifies that:
    - The function returns a sorted list of unique tags
    - All tags from all prompts are included
    """
    from apps.api.models import Prompt
    
    # Create prompts with various tags
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
    
    # Get all tags
    tags = get_all_tags(db_session)
    
    assert len(tags) == 6
    assert tags == sorted(tags)  # Verify sorted
    assert "git" in tags
    assert "workflow" in tags
    assert "automation" in tags
    assert "testing" in tags
    assert "deployment" in tags
    assert "ci-cd" in tags


def test_create_prompt_with_slug(db_session):
    """
    Test creating a prompt with an explicit slug.
    
    Verifies that:
    - The prompt is created with the specified slug
    - All fields are populated correctly
    - The prompt is persisted to the database
    """
    prompt_create = PromptCreate(
        slug="explicit-slug",
        title="Test Prompt",
        summary="A test prompt",
        difficulty="beginner",
        worksWith=["Chrome"],
        tags=["test"],
        targetSites=["example.com"],
        promptText="Test prompt text",
        steps=["Step 1"],
    )
    
    result = create_prompt(db_session, prompt_create)
    
    assert result.slug == "explicit-slug"
    assert result.title == "Test Prompt"
    assert result.summary == "A test prompt"
    assert result.difficulty == "beginner"
    assert result.worksWith == ["Chrome"]
    assert result.tags == ["test"]
    assert result.targetSites == ["example.com"]
    assert result.promptText == "Test prompt text"
    assert result.steps == ["Step 1"]
    assert result.id is not None
    assert result.createdAt is not None
    assert result.updatedAt is not None


def test_create_prompt_auto_slug(db_session):
    """
    Test creating a prompt with auto-generated slug from title.
    
    Verifies that:
    - The slug is auto-generated from the title
    - The slug is URL-friendly (lowercase, hyphens, no special chars)
    """
    prompt_create = PromptCreate(
        title="Test Auto Slug Prompt!",
        summary="A test prompt with auto slug",
        difficulty="beginner",
        worksWith=["Chrome"],
        tags=["test"],
        targetSites=["example.com"],
        promptText="Test prompt text",
        steps=["Step 1"],
    )
    
    result = create_prompt(db_session, prompt_create)
    
    assert result.slug == "test-auto-slug-prompt"
    assert result.title == "Test Auto Slug Prompt!"


def test_create_prompt_duplicate_slug(db_session):
    """
    Test creating a prompt with a duplicate slug.
    
    Verifies that:
    - The slug is made unique by appending a number
    """
    from apps.api.models import Prompt
    
    # Create first prompt
    prompt1 = Prompt(
        slug="duplicate-slug",
        title="First Prompt",
        summary="First prompt",
        difficulty="beginner",
        worksWith=["Chrome"],
        tags=["test"],
        targetSites=["example.com"],
        promptText="Test prompt text",
        steps=["Step 1"],
    )
    db_session.add(prompt1)
    db_session.commit()
    
    # Create second prompt with same slug
    prompt_create = PromptCreate(
        slug="duplicate-slug",
        title="Second Prompt",
        summary="Second prompt",
        difficulty="beginner",
        worksWith=["Chrome"],
        tags=["test"],
        targetSites=["example.com"],
        promptText="Test prompt text",
        steps=["Step 1"],
    )
    
    result = create_prompt(db_session, prompt_create)
    
    assert result.slug == "duplicate-slug-1"


def test_slugify_title():
    """
    Test the slugify_title helper function.
    
    Verifies that:
    - Titles are converted to lowercase
    - Spaces and underscores are replaced with hyphens
    - Special characters are removed
    - Consecutive hyphens are collapsed
    - Leading/trailing hyphens are removed
    """
    # Basic conversion
    assert slugify_title("Test Title") == "test-title"
    
    # With underscores
    assert slugify_title("Test_Title") == "test-title"
    
    # With special characters
    assert slugify_title("Test Title!") == "test-title"
    
    # With multiple spaces
    assert slugify_title("Test  Multiple   Spaces") == "test-multiple-spaces"
    
    # With special characters and numbers
    assert slugify_title("Test Title 123 @#$") == "test-title-123"
    
    # With leading/trailing spaces
    assert slugify_title("  Test Title  ") == "test-title"
    
    # With consecutive hyphens after conversion
    assert slugify_title("Test - Title") == "test-title"
    
    # Complex case
    assert slugify_title("My_Great_Title_123!!!") == "my-great-title-123"
