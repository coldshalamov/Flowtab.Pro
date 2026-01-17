# Flowtab.Pro Backend API

Backend API for Flowtab.Pro - A library of automated browser prompt recipes.

## Project Overview

The Flowtab.Pro backend is a RESTful API built with FastAPI that provides endpoints for managing a library of browser automation prompt recipes. It features:

- Fast, asynchronous API with automatic OpenAPI documentation
- SQLModel for type-safe database models and Pydantic schemas
- Alembic for database migrations
- PostgreSQL database
- CORS support for frontend integration
- Comprehensive test suite
- Docker support for containerized deployment

## Technology Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLModel** - SQLModel for database models and Pydantic schemas
- **Alembic** - Database migration tool
- **PostgreSQL** - Relational database
- **Uvicorn** - ASGI server
- **Pytest** - Testing framework

## Prerequisites

Before running the application, ensure you have the following installed:

- **Python 3.11+** - Download from [python.org](https://www.python.org/downloads/)
- **PostgreSQL** - Download from [postgresql.org](https://www.postgresql.org/download/)
- **pip** - Python package manager (included with Python)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Flowtab.Pro.git
cd Flowtab.Pro
```

### 2. Navigate to the API Directory

```bash
cd apps/api
```

### 3. Create a Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

### 1. Copy the Example Environment File

```bash
copy .env.example .env
```

**macOS/Linux:**
```bash
cp .env.example .env
```

### 2. Configure Environment Variables

Edit the `.env` file and configure the following variables:

```env
# Database connection URL
DATABASE_URL=postgresql://user:password@localhost:5432/flowtab

# Secret key for admin operations
ADMIN_KEY=your-secret-admin-key-here

# Comma-separated list of allowed CORS origins
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

**Note:** Replace `user`, `password`, and `flowtab` with your actual PostgreSQL credentials and database name. Generate a secure `ADMIN_KEY` using a password manager or a tool like `openssl rand -hex 32`.

## Database Setup

### 1. Create the Database

Connect to PostgreSQL and create the database:

```bash
psql -U postgres
CREATE DATABASE flowtab;
\q
```

### 2. Run Alembic Migrations

Apply all database migrations:

```bash
alembic upgrade head
```

This will create all necessary tables and indexes.

### 3. (Optional) Run Seed Script

Populate the database with sample data:

```bash
python seed.py
```

## Running the Application

### Development Mode

Run the API with hot-reload enabled:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Production Mode

Run the API with production settings:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Replace `$PORT` with your desired port (e.g., `8000`).

## API Documentation

The API provides auto-generated interactive documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Spec**: `http://localhost:8000/openapi.json`

These interfaces allow you to explore and test all API endpoints directly from your browser.

## Testing

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage Report

```bash
pytest --cov=.
```

### Run a Specific Test File

```bash
pytest tests/test_api.py
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests Matching a Pattern

```bash
pytest -k "test_create_prompt"
```

## Deployment

### Render.com

The project includes a `render.yaml` configuration file in the root directory for easy deployment to Render.com.

1. Push your code to a Git repository (GitHub, GitLab, etc.)
2. Connect your repository to [Render.com](https://render.com)
3. Render will automatically detect the `render.yaml` file and configure the deployment
4. Set the required environment variables in the Render dashboard

### Docker

The project includes a `Dockerfile` in the `apps/api` directory for containerized deployment.

**Build the Docker image:**

```bash
docker build -t flowtab-api .
```

**Run the container:**

```bash
docker run -p 8000:8000 --env-file .env flowtab-api
```

**Using Docker Compose:**

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/flowtab
      - ADMIN_KEY=${ADMIN_KEY}
      - CORS_ORIGINS=${CORS_ORIGINS}
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=flowtab
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Run with Docker Compose:

```bash
docker-compose up -d
```

## Project Structure

```
apps/api/
├── alembic/                 # Database migrations
│   ├── versions/           # Migration scripts
│   ├── env.py              # Alembic environment configuration
│   └── script.py.mako      # Migration template
├── tests/                  # Test suite
│   ├── conftest.py         # Pytest fixtures
│   ├── test_api.py         # API endpoint tests
│   └── test_crud.py        # CRUD operation tests
├── .env.example            # Example environment variables
├── .gitignore              # Git ignore rules
├── alembic.ini             # Alembic configuration
├── crud.py                 # CRUD operations
├── db.py                   # Database connection and initialization
├── Dockerfile              # Docker configuration
├── main.py                 # FastAPI application entry point
├── models.py               # SQLModel database models
├── pytest.ini              # Pytest configuration
├── requirements.txt        # Python dependencies
├── router.py               # API route definitions
├── schemas.py              # Pydantic schemas
├── seed.py                 # Database seeding script
└── settings.py             # Application settings
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:password@localhost:5432/flowtab` |
| `ADMIN_KEY` | Secret key for admin operations | `your-secret-admin-key-here` |
| `CORS_ORIGINS` | Comma-separated list of allowed origins | `http://localhost:3000,http://localhost:8000` |
| `TESTING` | Flag to indicate test environment (set by pytest) | `true` |

## Troubleshooting

### Database Connection Issues

**Problem:** `psycopg2.OperationalError: could not connect to server`

**Solutions:**
1. Ensure PostgreSQL is running: `pg_isready` or check the service status
2. Verify the `DATABASE_URL` in `.env` matches your PostgreSQL credentials
3. Check that the database exists: `psql -U postgres -l`
4. Ensure the user has proper permissions

### Migration Errors

**Problem:** Alembic migration fails or shows "target database is not up to date"

**Solutions:**
1. Check current migration status: `alembic current`
2. View migration history: `alembic history`
3. Reset migrations (use with caution in development):
   ```bash
   alembic downgrade base
   alembic upgrade head
   ```
4. If stuck, manually mark as current: `alembic stamp head`

### Port Already in Use

**Problem:** `Error: [Errno 48] Address already in use`

**Solutions:**
1. Find the process using the port:
   - **Windows:** `netstat -ano | findstr :8000`
   - **macOS/Linux:** `lsof -i :8000`
2. Kill the process or use a different port: `uvicorn main:app --port 8001`

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'sqlmodel'`

**Solutions:**
1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Verify Python version is 3.11+: `python --version`

### CORS Errors in Frontend

**Problem:** Browser shows CORS errors when calling the API

**Solutions:**
1. Check `CORS_ORIGINS` in `.env` includes your frontend URL
2. Ensure the origin matches exactly (including protocol and port)
3. For local development, include `http://localhost:3000` and `http://127.0.0.1:3000`

### Test Failures

**Problem:** Tests fail with database-related errors

**Solutions:**
1. Ensure test database is configured (uses in-memory SQLite by default)
2. Run tests with verbose output: `pytest -v`
3. Check test fixtures in `tests/conftest.py`
4. Ensure no other processes are accessing the database

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Pytest Documentation](https://docs.pytest.org/)

## License

This project is part of Flowtab.Pro. See the main repository for license information.
