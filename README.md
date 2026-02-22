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

Check out `.env.sample` for env examples

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

### Getting `external_id` (places) inside this API

Use our proxy endpoints (no auth required):

- List places: `GET /api/v1/external/places?limit=12&page=1`
- Search places: `GET /api/v1/external/places/search?q=Paris&limit=12&page=1`

Pick `data[i].id` from the response and use it as `external_id` when creating a project or adding a place.

You can now create a project **without places** (and add places later via `POST /api/v1/projects/{project_id}/places`).

### Docker

Build and run locally:

```bash
docker compose up --build
```

The compose file persists SQLite data in a named volume and sets:
- `DATABASE_URL=sqlite+aiosqlite:///./data/app.db`

### Postman collection

- **Public Postman collection**: [DevelopsToday test task – Travel Planner API](https://www.postman.com/joint-operations-observer-21402566/developstoday-test-task/collection/28806303-3853d7b5-bbcf-45ec-b2dd-dec97d497746)
- **Exported collection JSON (in this repo)**: [`Travel-Planner-API.postman_collection.json`](./Travel-Planner-API.postman_collection.json) (import it into Postman)

The collection is parameterized via `rootUrl` / `baseUrl` variables (defaults to `http://localhost:8000`).

It includes:
- Auth (`/auth/register`, `/auth/login`, `/auth/me`, `/auth/logout`)
- Users (`/users/me`, update name, update password)
- Projects CRUD (`/projects`)
- Project places (`/projects/{project_id}/places`)
- External places proxy (`/external/places`) to discover `external_id`

The Login request automatically extracts the `token` cookie and stores it as a collection variable, then uses it as `Authorization: Bearer {{token}}`.

### Third-party API cache (bonus)

The Art Institute API client caches successful `get_place(external_id)` responses in-memory (TTL + max size).

- `ARTIC_CACHE_ENABLED` (default `true`)
- `ARTIC_CACHE_TTL_SECONDS` (default `300`)
- `ARTIC_CACHE_MAX_ENTRIES` (default `1024`)

Note: Art Institute `places` IDs may be **negative** (example: `-2147472167`), so `external_id` is treated as a plain integer.
