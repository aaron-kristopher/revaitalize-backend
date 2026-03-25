# RevAItalize Backend

> :zap: This repository contains the backend (FastAPI) of the platform. The frontend lives in [revaitalize-frontend](https://github.com/aaron-kristopher/revaitalize-frontend).

## Prerequisites

- **Docker** and **Docker Compose** installed on your machine
- **Python 3.9+** (only required for local development)
- A **PostgreSQL** database (handled automatically by Docker Compose)

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/aaron-kristopher/revaitalize-backend.git
cd revaitalize-backend
```

### 2. Configure environment variables

Create a `.env` file in the project root. Copy the following template and fill in your values:

```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5433/revaidb
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

| Variable                  | Description                                      |
|---------------------------|--------------------------------------------------|
| `DATABASE_URL`            | PostgreSQL connection string                      |
| `SECRET_KEY`              | Secret key for JWT token signing (keep it safe)  |
| `ALGORITHM`               | JWT algorithm (default: `HS256`)                  |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry time in minutes (default: `30`)  |

## Running the Backend

### Recommended: Docker (works on Windows, macOS, Linux)

This starts both the database and the backend automatically.

```bash
docker compose up --build
```

The API will be available at **http://localhost:8001**.

### Local Development (optional)

If you prefer to run the backend directly on your machine (e.g., for debugging), you'll need a local PostgreSQL instance. Update `DATABASE_URL` in your `.env` to point to it.

```bash
# Install uv if you don't have it
pip install uv

# Install dependencies
uv pip install --system -r requirements.txt

# Run the dev server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at **http://localhost:8000**.

## Frontend Setup

The backend and frontend are separate repositories.

1. Clone the frontend:
   ```bash
   git clone https://github.com/aaron-kristopher/revaitalize-frontend.git
   ```

2. In your frontend's `.env.local` (or `.env`), point the API base URL to the backend:
   ```env
   VITE_API_BASE_URL=http://localhost:8001
   ```

3. Run the frontend:
   ```bash
   npm install
   npm run dev
   ```

## Database Migrations

This project uses **Alembic** for database migrations.

```bash
# Create a new migration
alembic revision --autogenerate -m "description of change"

# Run all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Check current migration
alembic current
```

On first startup, the backend automatically seeds the `exercises` table with default records, so no manual setup is required.

## API Documentation

FastAPI automatically generates interactive docs.

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## Project Structure

```
app/
  main.py              # FastAPI app entry point
  auth_routes.py       # Authentication endpoint (/token)
  security.py          # JWT & password utilities
  core/config.py       # Environment variable management
  db/
    database.py        # SQLAlchemy engine & session
    base.py            # Model aggregator for Alembic
  features/
    users/             # User, onboarding & problem CRUD
    exercises/         # Exercise CRUD
    sessions/          # Session, set & repetition CRUD
  prediction/
    routes.py          # LSTM inference endpoints
alembic/               # Database migrations
```

## Troubleshooting

### Port 8001 already in use

Change the mapped port in `compose.yaml`:

```yaml
ports:
  - "8080:8000"   # Use 8080 instead of 8001
```

Then update your frontend's `VITE_API_BASE_URL` to `http://localhost:8080`.

### Database connection refused

Make sure the `db` container is running:

```bash
docker compose ps
```

If it's not running, start it explicitly:

```bash
docker compose up db
```

### Migrations out of sync

Reset migrations by dropping all tables and re-running:

```bash
docker compose down -v   # WARNING: deletes all data
docker compose up --build
```
