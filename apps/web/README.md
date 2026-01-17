# Flowtab.Pro Frontend

Next.js application for browsing and searching automated browser prompt recipes.

## Tech Stack

- Next.js 15 (App Router)
- TypeScript
- Tailwind CSS v4
- shadcn/ui components
- Lucide React icons

## Getting Started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

Falls back to mock data if API is unavailable.

## Routes

- `/` - Home with featured prompts
- `/library` - Searchable library with filters
- `/p/[slug]` - Prompt detail page
- `/submit` - Submit new prompt (form only)

## Build

```bash
npm run build
npm start
```

## Deployment

Optimized for Vercel. Set `NEXT_PUBLIC_API_BASE` in environment variables.
