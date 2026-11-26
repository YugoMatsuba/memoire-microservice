# Backend structure

The backend follows [ADR 004](../docs/design/adr/004-backend-software-design.md),
with four layers directly under `app`.

```text
src/app/
├── main.py                     # Creates the app and registers routers
├── presentation/
│   ├── routes.py               # Aggregates endpoint routers
│   ├── endpoints/             # Health and authentication handlers
│   └── schemas/               # Pydantic request/response models
├── application/                # Services coordinating use cases
├── domain/                     # Entities, business rules, repository interfaces
└── infrastructure/
    ├── database.py             # SQLAlchemy Base, engine and session factory
    ├── models.py               # ORM models, including UserModel
    ├── users_repository.py     # Database operations and entity mapping
    └── security.py             # Argon2 hashing and JWT signing/verification
```

The domain contains the `User` dataclass and `UserRepository` contract. The
application contains `AuthenticationService`, its result/errors, and interfaces
for password hashing and token handling. Concrete security adapters live in
infrastructure; presentation dependencies wire them into services with one
database session per request.

## Authentication

- `POST /api/auth/register`: JSON email, password, username; returns HTTP 201.
- `POST /api/auth/login`: JSON email and password; returns HTTP 200.
- Both return `{ "user": { ... }, "access_token": "...", "token_type": "bearer" }`.
- `GET /api/auth/me`: pass `Authorization: Bearer <access_token>`; returns public
  user data, or HTTP 401 for a missing, invalid, expired, or deleted-user token.
- Registration returns 409 for an existing email. Invalid login credentials
  return the same 401 message for unknown email and incorrect password.

Emails are lowercased for account lookup and storage. Passwords use Argon2 hashes
and are never returned. Registration automatically signs the user in. The
repository's `add` operation owns the registration commit and rollback; database
uniqueness also handles concurrent duplicate registrations.

Access JWTs use HS256, user ID as `sub`, and a 15-minute lifetime. Set a random
`JWT_SECRET_KEY` of at least 32 bytes in the environment; no fallback key is used.
Generate and export a key in your terminal before starting the backend:

```bash
export JWT_SECRET_KEY="$(openssl rand -hex 32)"
docker compose up -d --build server
```

Keep that value stable for the running environment. Changing it invalidates
previously issued tokens. Docker Compose passes the exported value to the backend.
Rebuild the server image to install the new dependencies.

When running directly from `server/`, also set `DATABASE_URL` to your local
PostgreSQL URL (with `localhost:5433`, using `postgresql+psycopg://`). Apply
migrations before making authentication requests. Configuration is loaded
lazily; the health endpoint does not require database or JWT configuration.

Registration requires passwords of at least 16 characters in the API and browser
form; login accepts existing passwords. Successful browser submissions navigate
to a dummy welcome page, and failures display API errors.

Frontend token storage, refresh tokens, revocation, and rate
limiting are not implemented in this increment. Browser code must retain the
access token and send it on authenticated requests; a 401 can trigger navigation
to login. Use HTTPS for deployed authentication traffic.

## Layer responsibilities

- Presentation calls application services and translates between HTTP data and
  application inputs/results. Register its routers in `main.py`.
- Application services coordinate domain behavior through repository interfaces.
- Domain contains ordinary Python entities and repository contracts. Keep it
  independent of FastAPI, SQLAlchemy, and infrastructure implementations.
- Infrastructure implements repository contracts using SQLAlchemy and maps ORM
  objects to and from domain entities.

`main.py` assembles the application and can wire concrete infrastructure into
services. ORM models remain separate from domain entities and API schemas.

## Migrations

`alembic/` contains migration tooling and versioned schema changes. Its `env.py`
reads `DATABASE_URL` and uses `Base.metadata` as the desired schema. ORM models
are defined in `app/infrastructure/models.py`, which Alembic imports before
autogeneration. Existing migration files stay unchanged when application code
is reorganized.

From `server/`, with `DATABASE_URL` set:

```bash
uv run alembic revision --autogenerate -m "describe schema change"
# Review the generated migration before applying it.
uv run alembic upgrade head
```
