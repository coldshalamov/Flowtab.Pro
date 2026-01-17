# Flowtab.Pro

**A searchable library of automated browser prompt recipes for Comet, Playwright, and Opera Neon.**

Flowtab.Pro helps developers and automation engineers discover, share, and reuse battle-tested browser automation workflows. Browse prompts by difficulty, filter by tools, and copy ready-to-use recipes directly into your projects.

---

## 🚀 Quick Start

### Prerequisites
- **Node.js 18+** (for frontend)
- **Python 3.11+** (for backend)
- **PostgreSQL** (for database)

### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/Flowtab.Pro.git
cd Flowtab.Pro

# Frontend (Next.js)
cd apps/web
npm install
npm run dev
# → http://localhost:3000

# Backend (FastAPI)
cd apps/api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your DATABASE_URL
alembic upgrade head
python seed.py
uvicorn main:app --reload
# → http://localhost:8000
```

---

## 📁 Project Structure

```
Flowtab.Pro/
├── apps/
│   ├── web/              # Next.js frontend
│   │   ├── src/
│   │   │   ├── app/      # App Router pages
│   │   │   ├── components/  # React components
│   │   │   └── lib/      # API client, types, utils
│   │   └── public/       # Static assets
│   │
│   └── api/              # FastAPI backend
│       ├── alembic/      # Database migrations
│       ├── tests/        # Test suite
│       ├── models.py     # SQLModel database models
│       ├── schemas.py    # Pydantic schemas
│       ├── crud.py       # Database operations
│       ├── router.py     # API endpoints
│       └── seed.py       # Sample data
│
├── contracts/
│   └── openapi.yaml      # API specification
│
├── render.yaml           # Render.com deployment config
└── vercel.json           # Vercel deployment config
```

---

## 🛠️ Tech Stack

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS v4** - Styling
- **shadcn/ui** - Component library
- **Lucide Icons** - Icon set

### Backend
- **FastAPI** - Modern Python API framework
- **SQLModel** - Type-safe ORM
- **Alembic** - Database migrations
- **PostgreSQL** - Relational database
- **Pytest** - Testing framework

---

## 🌐 Deployment

### Recommended Setup
- **Frontend:** Vercel (free tier, optimized for Next.js)
- **Backend:** Render.com (free or $7/month for always-on)
- **Database:** Render PostgreSQL (free tier available)
- **Domain:** Point your domain DNS to Vercel and Render

### Environment Variables

**Frontend (Vercel):**
```bash
NEXT_PUBLIC_API_BASE=https://api.flowtab.pro
```

**Backend (Render):**
```bash
DATABASE_URL=postgresql://user:pass@host:5432/flowtab
ADMIN_KEY=your-secure-admin-key
CORS_ORIGINS=https://flowtab.pro,https://www.flowtab.pro
```

---

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI Spec:** `/contracts/openapi.yaml`

### Key Endpoints
- `GET /v1/prompts` - List prompts (with filters)
- `GET /v1/prompts/{slug}` - Get single prompt
- `GET /v1/tags` - List all tags
- `POST /v1/prompts` - Create prompt (admin only)

---

## 🧪 Testing

```bash
# Frontend
cd apps/web
npm run lint

# Backend
cd apps/api
pytest
pytest --cov=.  # With coverage
```

---

## 📖 Documentation

- **Frontend README:** `apps/web/README.md`
- **Backend README:** `apps/api/README.md`
- **API Contract:** `contracts/openapi.yaml`

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🔗 Links

- **Live Site:** https://flowtab.pro (coming soon)
- **API Docs:** https://api.flowtab.pro/docs (coming soon)
- **Issues:** https://github.com/yourusername/Flowtab.Pro/issues
