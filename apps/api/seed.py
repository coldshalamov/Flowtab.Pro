"""
Seed script for Flowtab.Pro backend API.

This script populates the database with example prompts for the automated
browser prompt recipe library.
"""

from sqlmodel import Session

from apps.api.crud import create_prompt, get_prompt_by_slug, get_user_by_email_or_username, create_user
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
        # Create superuser if it doesn't exist
        admin_email = "93robingattis@gmail.com"
        admin_username = "Coldshalamov"
        admin_password = "Alphonse5150$"
        existing_admin = get_user_by_email_or_username(session, admin_username)
        if not existing_admin:
            from apps.api.auth import get_password_hash
            from apps.api.schemas import UserCreate
            user_in = UserCreate(email=admin_email, username=admin_username, password=admin_password)
            hashed_pw = get_password_hash(admin_password)
            admin_user = create_user(session, user_create=user_in, hashed_password=hashed_pw)
            admin_user.is_superuser = True
            session.add(admin_user)
            session.commit()
            logger.info(f"👑 Created superuser: {admin_username} ({admin_email})")
        else:
            # Ensure the existing user is a superuser
            if not existing_admin.is_superuser:
                existing_admin.is_superuser = True
                session.add(existing_admin)
                session.commit()
                logger.info(f"👑 Promoted existing user to superuser: {existing_admin.username}")

        # Clear existing discussions (threads) if any, per user request to have an empty community
        from apps.api.models import Prompt
        from sqlmodel import delete
        
        # Delete all prompts with type="discussion"
        statement = delete(Prompt).where(Prompt.type == "discussion")
        session.exec(statement)
        session.commit()
        logger.info("🗑️ Cleared existing community threads (discussions)")

        # List of example prompts to seed
        # These are synced with the high-quality mock data used in the frontend
        prompts_data = [
            PromptCreate(
                slug="resolve-github-merge-conflicts",
                title="GitHub Conflict Resolution Shortcut",
                summary="Resolve all merge conflicts in one file as fast as possible by reading the full text via DOM, resolving intelligently, and pasting back the complete solution.",

                worksWith=[],
                tags=["featured", "dev", "github"],
                targetSites=["github.com"],
                promptText="""## **GitHub Conflict Resolution Shortcut - Optimized for Speed**

**Objective:** Resolve all merge conflicts in one file as fast as possible by reading the full text via DOM, resolving intelligently, and pasting back the complete solution.

***

### **Step 1: Extract the full conflicting file**

1. Locate the GitHub conflict editor (the editable code area showing the file).
2. Use `get_page_text` or `read_page` to extract the **entire file content** including all conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).
3. **Do NOT scroll, screenshot, or click individual "Accept current/incoming change" buttons.** Work entirely from the extracted text.

***

### **Step 2: Understand the codebase context**

This is a **React + wagmi + viem** project. The conflicts typically occur in React hooks, state declarations, and imports.

**Key principle:** Both branches usually add valid functionality. Your job is to **combine compatible changes** rather than discarding one side unless they're mutually exclusive.

***

### **Step 3: Resolve each conflict region intelligently**

For each conflict block:

```
<<<<<<< branch-a
current version
=======
incoming version
>>>>>>> branch-b
```

**Resolution rules:**

1. **Identical lines with different comments:** Keep the line once, preserve the more descriptive comment.
2. **New state variables or hooks:** If one branch adds a new `useState` or hook that doesn't conflict with existing code, **keep it**.
3. **Import changes:** Merge all unique imports from both sides. Remove duplicates.
4. **Logic changes:** If both sides modify the same function or JSX, analyze which change is more complete or combines both intents.

***

### **Step 4: Construct the resolved file**

- Remove **all** conflict markers.
- Ensure the file is valid JavaScript/TypeScript with correct syntax.
- Maintain consistent style (2-space indentation, single quotes).

***

### **Step 5: Replace editor content in one shot**

1. Select all text in the GitHub conflict editor (ctrl+a).
2. Paste the **entire resolved file** content.
3. **Self-check:** No markers remain, imports are correct, syntax is valid.

***

### **Step 6: Mark as resolved and complete the merge**

1. Click **"Mark as resolved"** button.
2. You'll be returned to the PR page automatically.
3. Click **"Merge PR"** or **"Squash and merge"** to complete.

**Do NOT commit prematurely.** Ensure all conflicts in all files are resolved first.""",
                steps=[
                    "Extract full conflicting file via DOM",
                    "Contextualize & resolve regions",
                    "Construct resolved file in memory",
                    "Replace editor content & mark resolved"
                ],
                notes="Both branches usually add valid functionality. Combine compatible changes rather than discarding one side.",
            ),
            PromptCreate(
                slug="amazon-price-tracker",
                title="Amazon Price Drop Alert",
                summary="Monitor any Amazon product page and get notified when the price drops below your target threshold.",

                worksWith=[],
                tags=["featured", "shopping", "monitoring"],
                targetSites=["amazon.com"],
                promptText="""## Amazon Price Drop Alert

**Objective:** Continuously monitor a product's price and trigger an alert when it drops.

### Steps:
1. Navigate to the Amazon product URL provided
2. Extract the current price from the buy box
3. Compare against the target threshold
4. If below threshold: Send notification via webhook
5. If above: Log the price and schedule next check

### Exit Condition:
Price drops below target OR monitoring period expires.""",
                steps=[
                    "Open product page",
                    "Extract current price",
                    "Compare to threshold",
                    "Send alert if triggered"
                ],
                notes="Set up a webhook endpoint to receive price alerts. Works with Slack, Discord, or email integrations.",
            ),
            PromptCreate(
                slug="linkedin-auto-apply",
                title="LinkedIn Easy Apply Automation",
                summary="Automatically apply to jobs matching your criteria using LinkedIn's Easy Apply feature.",

                worksWith=[],
                tags=["featured", "outreach", "jobs"],
                targetSites=["linkedin.com"],
                promptText="""## LinkedIn Easy Apply Automation

**Objective:** Streamline job applications by automating Easy Apply submissions.

### Pre-requisites:
- Logged into LinkedIn
- Resume uploaded to profile
- Search filters pre-configured

### Steps:
1. Navigate to Jobs with Easy Apply filter
2. For each job listing:
   - Click "Easy Apply"
   - Fill any required fields from profile data
   - Submit application
   - Log the job title and company
3. Move to next listing
4. Stop after N applications or end of results

### Safety:
- Add 5-10 second delays between applications
- Skip listings requiring additional questions""",
                steps=[
                    "Search for matching jobs",
                    "Click Easy Apply",
                    "Auto-fill application",
                    "Submit and log",
                    "Move to next"
                ],
                notes="Use responsibly. LinkedIn may rate-limit or flag automated activity.",
            ),
            PromptCreate(
                slug="google-sheets-web-scraper",
                title="Web Scrape to Google Sheets",
                summary="Extract structured data from any webpage and append it directly to a Google Sheet.",

                worksWith=[],
                tags=["featured", "scraping", "automation"],
                targetSites=["sheets.google.com"],
                promptText="""## Web Scrape to Google Sheets

**Objective:** Scrape data from a target page and write it to Google Sheets.

### Inputs:
- Target URL to scrape
- CSS selectors for data points
- Google Sheet URL

### Steps:
1. Navigate to target URL
2. Extract data using provided selectors
3. Format as row data
4. Navigate to Google Sheet
5. Append row to sheet
6. Confirm write successful

### Tips:
- Use browser DevTools to find selectors
- Test selectors on a single item first""",
                steps=[
                    "Load target page",
                    "Query selectors",
                    "Extract text content",
                    "Open Google Sheet",
                    "Append new row"
                ],
                notes="Requires Google login. Sheet must be editable by your account.",
            ),
            PromptCreate(
                slug="twitter-thread-unroller",
                title="Twitter Thread to Markdown",
                summary="Convert any Twitter/X thread into a clean, readable Markdown document.",

                worksWith=[],
                tags=["featured", "social", "productivity"],
                targetSites=["twitter.com", "x.com"],
                promptText="""## Twitter Thread to Markdown

**Objective:** Capture an entire thread and format it as Markdown.

### Steps:
1. Navigate to the first tweet in the thread
2. Scroll to load all replies from the author
3. Extract tweet text, images, and timestamps
4. Format as Markdown with proper headings
5. Copy to clipboard or save to file

### Output Format:
# Thread by @username

> Tweet 1 content

> Tweet 2 content

...""",
                steps=[
                    "Open thread URL",
                    "Scroll to load all tweets",
                    "Filter author's tweets only",
                    "Format as Markdown",
                    "Output to clipboard"
                ],
                notes="Works best on public threads. May need login for protected accounts.",
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
                prompt = create_prompt(session, prompt_data)
                
                # Mock like counts for initial quality seeding
                if prompt.slug == "resolve-github-merge-conflicts":
                    prompt.like_count = 19
                elif prompt.slug == "linkedin-auto-apply":
                    prompt.like_count = 18
                elif prompt.slug == "google-sheets-web-scraper":
                    prompt.like_count = 16
                elif prompt.slug == "amazon-price-tracker":
                    prompt.like_count = 14
                elif prompt.slug == "twitter-thread-unroller":
                    prompt.like_count = 7
                
                session.add(prompt)
                session.commit()
                
                logger.info(f"  ✅ Created prompt: {prompt_data.slug}")
                created_count += 1

        # Print summary
        logger.info("\n📊 Seed complete!")
        logger.info(f"  • Created: {created_count} prompts")
        logger.info(f"  • Skipped: {skipped_count} prompts (already exist)")
        logger.info(f"  • Total: {len(prompts_data)} prompts processed")


if __name__ == "__main__":
    main()

