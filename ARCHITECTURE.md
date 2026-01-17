# Flowtab.Pro - Architecture Overview

## System Design

**Flowtab.Pro** is a full-stack web application for discovering and sharing browser automation prompt recipes.

### Architecture Pattern
- **Monorepo** structure with separate frontend and backend apps
- **API-first** design with OpenAPI contract
- **Serverless-ready** deployment (Vercel + Render)

---

## Component Map

```
┌─────────────────────────────────────────────────────────┐
│                    USER BROWSER                         │
│                   (flowtab.pro)                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTPS
                     ▼
┌─────────────────────────────────────────────────────────┐
│              VERCEL (Frontend Host)                     │
│  ┌───────────────────────────────────────────────────┐  │
│  │         Next.js 15 App (SSR + Static)             │  │
│  │  • Home page (featured prompts)                   │  │
│  │  • Library (search/filter UI)                     │  │
│  │  • Detail pages (prompt view)                     │  │
│  │  • Submit form                                    │  │
│  └────────────────────┬──────────────────────────────┘  │
└───────────────────────┼─────────────────────────────────┘
                        │
                        │ REST API
                        │ (api.flowtab.pro)
                        ▼
┌─────────────────────────────────────────────────────────┐
│              RENDER (Backend Host)                      │
│  ┌───────────────────────────────────────────────────┐  │
│  │           FastAPI Application                     │  │
│  │  • GET /v1/prompts (list with filters)            │  │
│  │  • GET /v1/prompts/{slug} (single)                │  │
│  │  • GET /v1/tags (all tags)                        │  │
│  │  • POST /v1/prompts (admin only)                  │  │
│  └────────────────────┬──────────────────────────────┘  │
└───────────────────────┼─────────────────────────────────┘
                        │
                        │ SQL
                        ▼
┌─────────────────────────────────────────────────────────┐
│           RENDER PostgreSQL Database                    │
│  • prompts table (JSON columns for arrays)             │
│  • Alembic migrations for schema versioning            │
└─────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. User Visits Homepage
```
Browser → Vercel (Next.js SSR) → Render API → PostgreSQL
       ← Featured Prompts (3 items) ←────────←
```

### 2. User Searches Library
```
Browser → Vercel (Client-side filter update)
       → Render API /v1/prompts?q=automation&difficulty=beginner
       ← Filtered Results ←
```

### 3. User Views Prompt Detail
```
Browser → Vercel (SSR) → Render API /v1/prompts/playwright-basics
       ← Full Prompt Data ←
```

---

## Tech Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 15 | Server-side rendering + static generation |
| **Styling** | Tailwind CSS v4 | Utility-first CSS |
| **Components** | shadcn/ui | Accessible React components |
| **Backend** | FastAPI | High-performance Python API |
| **ORM** | SQLModel | Type-safe database models |
| **Database** | PostgreSQL | Relational data storage |
| **Migrations** | Alembic | Schema version control |
| **Hosting (FE)** | Vercel | Serverless Next.js deployment |
| **Hosting (BE)** | Render | Managed Python hosting |

---

## Key Design Decisions

### 1. **Monorepo Structure**
- **Why:** Shared types, single deployment pipeline, easier refactoring
- **Tradeoff:** Slightly more complex build configuration

### 2. **JSON Columns for Arrays**
- **Why:** PostgreSQL JSON columns allow flexible querying without joins
- **Tradeoff:** Slightly more complex filtering logic in CRUD layer

### 3. **Mock Data Fallback**
- **Why:** Frontend works even if backend is down (development + resilience)
- **Tradeoff:** Need to keep mock data in sync with API contract

### 4. **Serverless Deployment**
- **Why:** Zero DevOps overhead, auto-scaling, free tier available
- **Tradeoff:** Cold starts on free tier (15min sleep on Render)

### 5. **Admin-Only Submissions**
- **Why:** Quality control, prevent spam
- **Tradeoff:** Requires manual moderation workflow

---

## File Organization

### Frontend (`apps/web/src/`)
```
app/
├── layout.tsx          # Root layout with header/footer
├── page.tsx            # Home page (featured prompts)
├── library/page.tsx    # Search/filter page
├── p/[slug]/page.tsx   # Dynamic prompt detail
└── submit/page.tsx     # Submission form

components/
├── PromptCard.tsx      # Reusable prompt card
├── SearchAndFilters.tsx # Filter UI with URL sync
├── SiteHeader.tsx      # Navigation
└── SiteFooter.tsx      # Footer with links

lib/
├── api.ts              # API client with mock fallback
├── apiTypes.ts         # TypeScript interfaces
└── mockData.ts         # Fallback data
```

### Backend (`apps/api/`)
```
models.py      # SQLModel database schema
schemas.py     # Pydantic request/response models
crud.py        # Database operations
router.py      # API endpoint definitions
main.py        # FastAPI app initialization
seed.py        # Sample data script
alembic/       # Database migrations
tests/         # Pytest test suite
```

---

## Environment Configuration

### Frontend (Vercel)
```bash
NEXT_PUBLIC_API_BASE=https://api.flowtab.pro
```

### Backend (Render)
```bash
DATABASE_URL=postgresql://user:pass@host:5432/flowtab
ADMIN_KEY=<secure-random-key>
CORS_ORIGINS=https://flowtab.pro,https://www.flowtab.pro
```

---

## Deployment Workflow

1. **Push to GitHub** → Triggers builds
2. **Vercel** auto-deploys frontend from `apps/web`
3. **Render** auto-deploys backend from `apps/api` (via `render.yaml`)
4. **Alembic migrations** run manually on Render shell
5. **DNS** points `flowtab.pro` → Vercel, `api.flowtab.pro` → Render

---

## For LLM Agents

When working on this codebase:
- **Frontend changes:** Edit files in `apps/web/src/`
- **Backend changes:** Edit files in `apps/api/`
- **API contract:** Update `contracts/openapi.yaml` first
- **Database changes:** Create Alembic migration, update `models.py`
- **Testing:** Run `npm run lint` (frontend) and `pytest` (backend)
- **Deployment:** Changes auto-deploy on push to `main`

The project follows **API-first design** — always check the OpenAPI spec before implementing features.
