"""
Seed script for Flowtab.Pro backend API.

This script populates the database with example prompts for the automated
browser prompt recipe library.
"""

from sqlmodel import Session

from apps.api.crud import create_prompt, get_prompt_by_slug
from apps.api.db import engine
from apps.api.schemas import PromptCreate


import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """
    Main function to seed the database with example prompts.
    """
    logger.info("🌱 Starting database seed...")

    # Create database session
    with Session(engine) as session:
        # List of example prompts to seed
        prompts_data = [
            # Required prompts
            PromptCreate(
                slug="auto-merge-preview-branches",
                title="Auto-merge preview branches to avoid stale Jules edits",
                summary="Automatically merge preview branches to keep Jules edits fresh and avoid conflicts",
                difficulty="intermediate",
                worksWith=["GitHub", "Git", "CI/CD"],
                tags=["git", "workflow", "automation", "merge", "preview"],
                targetSites=["github.com"],
                promptText="Automatically merge preview branches when all checks pass to prevent stale Jules edits and maintain a clean development workflow.",
                steps=[
                    "Navigate to the repository's Actions tab",
                    "Configure a workflow to trigger on pull request updates",
                    "Set up conditional merge rules based on check status",
                    "Enable auto-merge for preview branches only",
                    "Monitor merge results in the Actions log",
                ],
                notes="Only use for preview branches, not main or production branches.",
            ),
            PromptCreate(
                slug="resolve-github-conflict-markers",
                title="Resolve GitHub conflict markers via DOM-copy workflow",
                summary="Step-by-step workflow to resolve merge conflicts by copying DOM elements from the conflicting version",
                difficulty="advanced",
                worksWith=["GitHub", "VS Code", "Git"],
                tags=["git", "conflict-resolution", "workflow", "advanced"],
                targetSites=["github.com"],
                promptText="Resolve GitHub merge conflict markers by using a DOM-copy workflow that preserves the correct changes while maintaining file integrity.",
                steps=[
                    "Open the conflicted file in GitHub's web interface",
                    "Identify the conflict markers (<<<<<<<, =======, >>>>>>>)",
                    "Review both sides of the conflict",
                    "Copy the desired content using DOM inspection tools",
                    "Paste the resolved content into your local editor",
                    "Remove all conflict markers",
                    "Stage and commit the resolved file",
                ],
                notes="Always verify the resolved file before committing to ensure no unintended changes were introduced.",
            ),
            PromptCreate(
                slug="rendercom-deploy-api-key-wiring",
                title="Render.com deploy + API key wiring checklist",
                summary="Complete checklist for deploying to Render.com and properly wiring API keys",
                difficulty="intermediate",
                worksWith=["Render.com", "GitHub", "CLI"],
                tags=["deployment", "render", "api-keys", "checklist"],
                targetSites=["render.com", "github.com"],
                promptText="A comprehensive checklist for deploying applications to Render.com and ensuring all API keys are properly configured and wired.",
                steps=[
                    "Create a new web service on Render.com",
                    "Connect your GitHub repository",
                    "Configure build and start commands",
                    "Add all required environment variables in Render dashboard",
                    "Verify API key format and encoding",
                    "Test API key access in the deployed application",
                    "Set up automatic deployments on push to main",
                    "Monitor deployment logs for any configuration issues",
                ],
                notes="Keep a secure backup of all API keys in a password manager.",
            ),
            PromptCreate(
                slug="playwright-mcp-stable-selectors",
                title="Playwright MCP: stable selectors + retry strategy",
                summary="Best practices for creating stable selectors and implementing retry strategies in Playwright MCP",
                difficulty="advanced",
                worksWith=["Playwright", "MCP", "VS Code"],
                tags=["playwright", "mcp", "selectors", "testing", "retry"],
                targetSites=["playwright.dev", "github.com"],
                promptText="Implement stable selectors and robust retry strategies in Playwright MCP to ensure reliable browser automation across different environments.",
                steps=[
                    "Use data-testid attributes for element identification",
                    "Prefer role-based selectors over CSS classes",
                    "Implement explicit waits with reasonable timeouts",
                    "Add retry logic with exponential backoff",
                    "Log selector failures for debugging",
                    "Test selectors across different browsers",
                    "Use locator assertions for better error messages",
                ],
                notes="Avoid using auto-generated IDs or dynamic class names as selectors.",
            ),
            # Additional example prompts
            PromptCreate(
                slug="automated-pr-review-checklist",
                title="Automated PR review checklist with diff analysis",
                summary="Automated pull request review process that analyzes diffs and checks against a predefined checklist",
                difficulty="intermediate",
                worksWith=["GitHub", "Git", "CI/CD"],
                tags=["pr-review", "automation", "code-quality", "checklist"],
                targetSites=["github.com"],
                promptText="Automatically review pull requests by analyzing code diffs and checking against a comprehensive quality checklist.",
                steps=[
                    "Trigger the review bot on PR creation or update",
                    "Fetch the diff between base and head branches",
                    "Analyze changed files for common issues",
                    "Check against style guide and linting rules",
                    "Verify test coverage for new code",
                    "Review documentation updates",
                    "Post review comments as GitHub checks",
                    "Block merge if critical issues are found",
                ],
                notes="Customize the checklist based on your team's specific requirements.",
            ),
            PromptCreate(
                slug="local-environment-setup-nextjs-fastapi",
                title="Local environment setup for Next.js + FastAPI monorepo",
                summary="Step-by-step guide for setting up a local development environment with Next.js frontend and FastAPI backend",
                difficulty="beginner",
                worksWith=["Node.js", "Python", "VS Code", "Docker"],
                tags=["setup", "nextjs", "fastapi", "monorepo", "development"],
                targetSites=["nextjs.org", "fastapi.tiangolo.com"],
                promptText="Complete local development environment setup for a monorepo containing Next.js frontend and FastAPI backend applications.",
                steps=[
                    "Clone the repository to your local machine",
                    "Install Node.js version 18 or higher",
                    "Install Python 3.10 or higher",
                    "Navigate to the frontend directory and run npm install",
                    "Navigate to the backend directory and create a virtual environment",
                    "Activate the virtual environment and install Python dependencies",
                    "Copy .env.example files and configure environment variables",
                    "Start the FastAPI backend with uvicorn",
                    "Start the Next.js frontend with npm run dev",
                    "Verify both services are running and communicating",
                ],
                notes="Use Docker Compose for an easier setup if available.",
            ),
            PromptCreate(
                slug="docker-compose-development-workflow",
                title="Docker Compose development workflow",
                summary="Efficient development workflow using Docker Compose for multi-container applications",
                difficulty="intermediate",
                worksWith=["Docker", "Docker Compose", "VS Code"],
                tags=["docker", "development", "workflow", "containers"],
                targetSites=["docs.docker.com"],
                promptText="Streamline your development workflow with Docker Compose for managing multi-container applications with hot-reload and volume mounting.",
                steps=[
                    "Create a docker-compose.yml file in your project root",
                    "Define services for your application, database, and other dependencies",
                    "Configure volume mounts for hot-reload during development",
                    "Set up environment variables in the compose file",
                    "Create a Dockerfile for each service with development optimizations",
                    "Use docker-compose up to start all services",
                    "Use docker-compose logs to monitor service output",
                    "Use docker-compose down to stop and clean up services",
                ],
                notes="Use .dockerignore files to exclude unnecessary files from build context.",
            ),
            PromptCreate(
                slug="database-migration-testing-strategy",
                title="Database migration testing strategy",
                summary="Comprehensive strategy for testing database migrations safely before production deployment",
                difficulty="advanced",
                worksWith=["Alembic", "PostgreSQL", "Docker", "CI/CD"],
                tags=["database", "migration", "testing", "alembic", "postgresql"],
                targetSites=["alembic.sqlalchemy.org", "postgresql.org"],
                promptText="A thorough testing strategy for database migrations that ensures data integrity and minimal downtime during production deployments.",
                steps=[
                    "Create a new migration with alembic revision",
                    "Write the upgrade and downgrade SQL changes",
                    "Test migration on a fresh local database",
                    "Verify data integrity after migration",
                    "Test the downgrade path to ensure reversibility",
                    "Run migration on a staging environment with production-like data",
                    "Perform performance testing on large datasets",
                    "Create a rollback plan before production deployment",
                    "Monitor database metrics during production migration",
                ],
                notes="Always have a recent backup before running migrations in production.",
            ),
        ]

        # Track statistics
        created_count = 0
        skipped_count = 0

        # Insert each prompt
        for prompt_data in prompts_data:
            # Check if prompt already exists by slug
            existing_prompt = get_prompt_by_slug(session, prompt_data.slug)

            if existing_prompt:
                logger.info(f"  ⏭️  Skipping existing prompt: {prompt_data.slug}")
                skipped_count += 1
            else:
                # Create the prompt
                create_prompt(session, prompt_data)
                logger.info(f"  ✅ Created prompt: {prompt_data.slug}")
                created_count += 1

        # Print summary
        logger.info("\n📊 Seed complete!")
        logger.info(f"  • Created: {created_count} prompts")
        logger.info(f"  • Skipped: {skipped_count} prompts (already exist)")
        logger.info(f"  • Total: {len(prompts_data)} prompts processed")


if __name__ == "__main__":
    main()
