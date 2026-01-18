# Flowtab.Pro Comprehensive Plan

Date: 2026-01-18

## 0) Current Snapshot (What’s Done)

### Backend (FastAPI + SQLModel)
- Auth: email/password registration + JWT login (`/v1/auth/register`, `/v1/auth/token`, `/v1/users/me`).
- Admin bootstrap: promote user to superuser via `POST /v1/users/promote` gated by `X-Admin-Key`.
- OAuth (Google/GitHub/Facebook):
  - `POST /v1/auth/oauth/{provider}/start` returns `{ authorize_url, state, code_verifier, code_challenge }`
  - `POST /v1/auth/oauth/{provider}/exchange` validates state + redirect allowlist + PKCE, creates user+oauth account, returns JWT
  - `POST /v1/auth/oauth/{provider}/link` links provider to an already-authenticated user
- Prompts: list/search/filter/paginate; create requires auth; delete requires superuser.
- Forum (minimal): prompt-based comments implemented:
  - `GET /v1/prompts/{slug}/comments` (public)
  - `POST /v1/prompts/{slug}/comments` (auth)
  - `DELETE /v1/comments/{comment_id}` (author or superuser)
- Security hardening already applied:
  - OAuth: state validation + redirect URI allowlist + PKCE enforcement
  - Comments: HTML escaping on input (XSS mitigation) + basic (in-memory) rate limits
- Backend tests: `python -m pytest -q` passes.

### Frontend (Next.js App Router)
- Routes exist: `apps/web/src/app/{login,register,library,submit,p/[slug],privacy,terms}`.
- Uses an AuthProvider with JWT in localStorage.
- Missing UI wiring:
  - OAuth buttons + callback handling
  - Comments UI on prompt detail pages
  - Admin dashboard/controls beyond any small components

### Repo Hygiene
- Root `flowtab.db` exists.
- `apps/api/venv/` exists and appears tracked (should not be in git).
- Missing `apps/api/.env.example` documenting required env vars.

## 1) Product Spec (Target)

### Roles
- Guest: browse Flows (prompts), read comments.
- User: create account (email/password or OAuth), submit Flows, comment.
- Admin (superuser): delete any Flow, delete any comment, promote users.

### Authentication Requirements
- Google auth
- GitHub auth
- Facebook auth
- Email/password auth (already)

### Forum Requirements
- Users can post and discuss.
- MVP approach: treat each Flow as a “thread”; comments are “posts”.

### Branding Requirement
- Replace user-facing “Prompt” wording with “Flow”.
- Decision (MVP): keep API/DB stable (`/prompts`, `promptText`, `prompts` table) and rename only UI/marketing copy.

## 2) Architecture Decisions (Keep It Simple)

### Auth Model
- Backend remains the source of truth.
- Frontend stores a JWT and sends `Authorization: Bearer <token>`.
- OAuth uses the backend-centric `start -> provider redirect -> exchange` flow (already implemented).

### Forum Model
- MVP is Comment-only (thread = prompt). No separate “forum post” entity yet.
- Add a separate `ForumPost` only if you need non-prompt discussions.

### Admin Model
- Use `is_superuser` already in User table.
- Admin bootstrap remains via `X-Admin-Key` promote endpoint (documented, protected).

## 3) Milestones (Phased Execution)

### Phase A — Repo Hygiene + Baselines (1 day)
Acceptance:
- Backend tests pass.
- Frontend builds.
- No tracked venv or local DB artifacts.

Tasks:
- Remove/stop tracking `apps/api/venv/`.
- Add `flowtab.db` to `.gitignore` (or remove entirely).
- Add `apps/api/.env.example`.
- Add `apps/web/.env.example` for `NEXT_PUBLIC_API_BASE`.

### Phase B — OAuth UI (1–2 days)
Acceptance:
- Login page offers Google/GitHub/Facebook.
- Callback completes and user is logged in.

Tasks:
- Add OAuth buttons to `apps/web/src/app/login/page.tsx`.
- Add callback route, e.g. `apps/web/src/app/auth/callback/page.tsx`.
- Implement:
  1) call `POST /v1/auth/oauth/{provider}/start?redirect_uri=...`
  2) redirect user to returned `authorize_url`
  3) on callback, call `POST /v1/auth/oauth/{provider}/exchange` with `{ code, redirect_uri, state, code_verifier }`
  4) store JWT, redirect to `/library`.

### Phase C — Comments UI (0.5–1 day)
Acceptance:
- Prompt detail shows comments list.
- Authenticated user can post.
- Author/admin can delete.

Tasks:
- Update `apps/web/src/app/p/[slug]/page.tsx` to fetch and display comments.
- Create components:
  - `CommentList`
  - `CommentForm`
  - `CommentItem`
- Add API client helpers in `apps/web/src/lib/api.ts`.

### Phase D — Admin UX (1–2 days)
Acceptance:
- Admin can view prompts, delete prompts, and moderate comments.
- Admin can promote users.

Tasks:
- Add `/admin` route and navigation for superusers.
- Add Users view:
  - list users (requires adding a backend endpoint if missing: `GET /v1/users` superuser-only)
  - promote user (call existing `/v1/users/promote` but consider requiring superuser token + admin key, or replace with superuser-only promote without admin key once bootstrapped)

### Phase E — Branding: “Prompt” -> “Flow” (0.5–1 day)
Acceptance:
- All user-facing copy says “Flow”.

Tasks:
- Search/replace UI strings in `apps/web/src`.
- Keep API field names unchanged (`promptText`, `/prompts`).
- Optionally add alias endpoints (`/v1/flows`) later without breaking `/v1/prompts`.

### Phase F — Production Readiness (1–2 days)
Acceptance:
- OAuth works on prod domains.
- Secrets managed.
- Multi-worker safe (or documented limitations).

Tasks:
- Configure production env vars.
- Add security headers at the edge (Vercel) and/or API middleware.
- Move in-memory OAuth state + rate limits to Redis for multi-worker.

## 4) Testing Strategy

### Backend
- Continue pytest-based integration tests:
  - OAuth: start/exchange/link and edge cases (expired state, redirect allowlist reject)
  - Comments: spam/rate-limit behavior, superuser delete
  - Admin: superuser protections on delete and user listing/promote

Commands:
- `cd apps/api && python -m pytest -q`

### Frontend
- Add Playwright e2e (recommended) to cover:
  - Register/login (email/password)
  - OAuth flow (can be partially mocked; full provider flows require secrets)
  - Create Flow + comment
  - Admin delete

Commands (to be added):
- `cd apps/web && npm run test:e2e`

## 5) Deployment & Env Vars

### Backend env (Render or similar)
- `DATABASE_URL`
- `SECRET_KEY` (JWT)
- `ADMIN_KEY` (bootstrap promote)
- `CORS_ORIGINS`
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`
- `FACEBOOK_CLIENT_ID`, `FACEBOOK_CLIENT_SECRET`
- `OAUTH_REDIRECT_ALLOWLIST` (comma-separated)

### Frontend env (Vercel)
- `NEXT_PUBLIC_API_BASE`

OAuth callback URLs:
- Decide one canonical callback URL, e.g. `https://flowtab.pro/auth/callback?provider=google`.

## 6) Security Execution Plan (Repo-Specific)

### Known Risks
- Multi-worker: in-memory OAuth state and in-memory rate limits will break or become bypassable.
- JWT storage: localStorage is vulnerable to XSS; prefer HttpOnly cookies if/when feasible.

### P0 (Must do for real production)
- Move OAuth state store to Redis.
- Move rate limiting to Redis (at least auth + comment create).
- Ensure `SECRET_KEY` is not default and rotated via env.
- Add security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options).

### P1
- Add audit logging for admin actions and auth failures.
- Add brute-force protection for `/auth/token`.

### P2
- Consider refresh tokens and server-side session invalidation.
- Add content moderation/spam mitigation.

## 7) Open Questions
- Do we want a dedicated Forum section (non-prompt threads), or is comment-only enough for MVP?
- Do we want to rename API routes/DB (high risk) or keep “prompts” internally forever (recommended for now)?
- Do we want cookie-based auth in the web app (more secure), or accept JWT localStorage for MVP?
