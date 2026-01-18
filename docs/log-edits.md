# Edit Log

## 2026-01-18
- Updated backend to associate created prompts with a user `author_id`.
- Updated `/v1/prompts` creation to require bearer auth and set `author_id` from the authenticated user.
- Fixed DELETE route to return proper `204 No Content` without violating FastAPI response rules.
- Updated backend tests to use real register/login flow instead of `X-Admin-Key` for prompt creation.
- Pinned `bcrypt==4.1.3` for Python 3.13 compatibility with passlib.
- Implemented OAuth start/exchange/link endpoints with CSRF/state validation, PKCE, and redirect URI allowlist.
- Added `oauth_accounts` table + unique constraint on `(provider, provider_user_id)` and an Alembic migration.
- Implemented forum-style comments on prompts (create/list/delete) + tests + Alembic migration.
- Hardened comments against stored XSS by HTML-escaping comment bodies and added best-effort in-memory rate limits for comment create/delete.
