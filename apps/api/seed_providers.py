"""
Seed script for AI providers.

Run this to populate the providers table with default AI providers.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, create_engine, select
from models import Provider

from settings import settings


def seed_providers():
    """Seed the database with AI providers."""
    engine = create_engine(settings.database_url)

    providers_data = [
        {
            "name": "zai",
            "slug": "zai",
            "display_name": "Z.ai",
            "description": "Zhipu AI - Chinese AI provider with advanced language models",
            "api_endpoint": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            "auth_type": "api_key",
            "supports_api_key": True,
            "supports_oauth": False,
            "supports_manual": True,
            "rate_limit_per_minute": 100,
            "rate_limit_per_hour": 5000,
        },
        {
            "name": "claude_code",
            "slug": "claude-code",
            "display_name": "Claude Code",
            "description": "Anthropic Claude - Advanced AI assistant for coding and analysis",
            "api_endpoint": "https://api.anthropic.com/v1/messages",
            "auth_type": "api_key",
            "supports_api_key": True,
            "supports_oauth": False,
            "supports_manual": True,
            "rate_limit_per_minute": 50,
            "rate_limit_per_hour": 1000,
        },
        {
            "name": "codex",
            "slug": "codex",
            "display_name": "OpenAI Codex",
            "description": "OpenAI's code generation model",
            "api_endpoint": "https://api.openai.com/v1/chat/completions",
            "auth_type": "api_key",
            "supports_api_key": True,
            "supports_oauth": False,
            "supports_manual": True,
            "rate_limit_per_minute": 60,
            "rate_limit_per_hour": 3000,
        },
        {
            "name": "moonshot_kimi",
            "slug": "moonshot-kimi",
            "display_name": "Moonshot Kimi",
            "description": "Moonshot AI's Kimi - Chinese AI assistant with long context window",
            "api_endpoint": "https://api.moonshot.cn/v1/chat/completions",
            "auth_type": "api_key",
            "supports_api_key": True,
            "supports_oauth": False,
            "supports_manual": True,
            "rate_limit_per_minute": 20,
            "rate_limit_per_hour": 1000,
        },
        {
            "name": "minimax",
            "slug": "minimax",
            "display_name": "MiniMax",
            "description": "MiniMax AI - Chinese provider with text and image models",
            "api_endpoint": "https://api.minimax.chat/v1/text/chatcompletion_v2",
            "auth_type": "api_key",
            "supports_api_key": True,
            "supports_oauth": False,
            "supports_manual": True,
            "rate_limit_per_minute": 30,
            "rate_limit_per_hour": 2000,
        },
        {
            "name": "github_copilot",
            "slug": "github-copilot",
            "display_name": "GitHub Copilot",
            "description": "GitHub's AI-powered code completion assistant",
            "api_endpoint": None,
            "auth_type": "oauth",
            "supports_api_key": False,
            "supports_oauth": True,
            "supports_manual": True,
            "documentation_url": "https://docs.github.com/en/copilot",
        },
        {
            "name": "grok",
            "slug": "grok",
            "display_name": "Grok",
            "description": "xAI's Grok AI assistant with real-time information",
            "api_endpoint": "https://api.x.ai/v1/chat/completions",
            "auth_type": "api_key",
            "supports_api_key": True,
            "supports_oauth": False,
            "supports_manual": True,
            "rate_limit_per_minute": 50,
            "rate_limit_per_hour": 2000,
        },
        {
            "name": "gemini",
            "slug": "gemini",
            "display_name": "Google Gemini",
            "description": "Google's multimodal AI assistant",
            "api_endpoint": "https://generativelanguage.googleapis.com/v1beta/models",
            "auth_type": "api_key",
            "supports_api_key": True,
            "supports_oauth": False,
            "supports_manual": True,
            "rate_limit_per_minute": 60,
            "rate_limit_per_hour": 1500,
        },
        {
            "name": "antigravity",
            "slug": "antigravity",
            "display_name": "Google Antigravity",
            "description": "Google's advanced AI research model",
            "api_endpoint": None,
            "auth_type": "api_key",
            "supports_api_key": True,
            "supports_oauth": False,
            "supports_manual": True,
            "documentation_url": "https://ai.google.dev/research",
        },
    ]

    with Session(engine) as session:
        # Check if providers already exist
        existing_providers = session.exec(select(Provider)).all()
        existing_slugs = {p.slug for p in existing_providers}

        print(f"Found {len(existing_providers)} existing providers")

        added_count = 0
        updated_count = 0
        skipped_count = 0

        for provider_data in providers_data:
            slug = provider_data["slug"]

            if slug in existing_slugs:
                # Update existing provider
                existing = session.exec(
                    select(Provider).where(Provider.slug == slug)
                ).first()

                # Update fields
                for key, value in provider_data.items():
                    if key != "slug":  # Don't update the slug
                        setattr(existing, key, value)

                session.add(existing)
                updated_count += 1
                print(f"  ✓ Updated: {provider_data['display_name']}")
            else:
                # Create new provider
                provider = Provider(**provider_data)
                session.add(provider)
                added_count += 1
                print(f"  + Added: {provider_data['display_name']}")

        try:
            session.commit()
            print(f"\n✓ Seeding complete!")
            print(f"  Added: {added_count}")
            print(f"  Updated: {updated_count}")
            print(f"  Total providers: {len(existing_providers) + added_count}")
        except Exception as e:
            session.rollback()
            print(f"\n✗ Error during seeding: {e}")
            raise


if __name__ == "__main__":
    seed_providers()
