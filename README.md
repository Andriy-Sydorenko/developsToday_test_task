## Travel Planner API (DevelopsToday test task)

FastAPI CRUD application for managing **travel projects** and **places** (validated via the Art Institute of Chicago public API).

### Tech

- **FastAPI**
- **SQLAlchemy 2.x (async)** + **SQLite**
- **Alembic** migrations
- **JWT auth** (cookie-based)

### Requirements

- **Python 3.12**

### Setup

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
```

### Configuration

The app uses `pydantic-settings` and reads `.env` (optional). Common options:

- **`DATABASE_URL`**: defaults to `sqlite+aiosqlite:///./app.db`
- **`JWT_SECRET`**: defaults to `CHANGE-ME-IN-PRODUCTION`
- **`ARTIC_API_BASE_URL`**: defaults to `https://api.artic.edu/api/v1`
- **`ARTIC_API_TIMEOUT_SECONDS`**: defaults to `10.0`
- **`IS_PRODUCTION`**: defaults to `false`

Example `.env`:

```bash
DATABASE_URL=sqlite+aiosqlite:///./app.db
JWT_SECRET=dev-secret
IS_PRODUCTION=false
```

### Database migrations

Run Alembic migrations:

```bash
alembic upgrade head
```

### Run the API

```bash
uvicorn main:app --reload
```

API base path: `http://localhost:8000/api/v1`  
Swagger/OpenAPI: `http://localhost:8000/docs`

### Postman collection

- [DevelopsToday test task – Postman request](https://www.postman.com/joint-operations-observer-21402566/developstoday-test-task/request/28806303-7ecb2b90-ebf4-46dd-9d55-6b0381f4f473)

It includes:
- Auth (`/auth/register`, `/auth/login`, `/auth/me`, `/auth/logout`)
- Projects CRUD (`/projects`)
- Project places (`/projects/{project_id}/places`)

The Login request automatically extracts the `token` cookie and stores it as a collection variable, then uses it as `Authorization: Bearer {{token}}`.
