# Pure Lioraa — E-Commerce Platform

B2C beauty-products e-commerce platform (Hair/Face/Body/Skin/Personal Care)
with an AI product-assistant chatbot (AWS Bedrock + RAG).

- **Backend**: [`backend/`](backend) — Python 3.12, FastAPI, PostgreSQL + pgvector.
  See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full feature-based
  architecture, data model, and technology mapping against the PRD.
- **Frontend**: React (not yet scaffolded in this repo).

## Quickstart

```bash
cp .env.example .env                    # postgres + pgAdmin credentials for docker-compose
cp backend/.env.example backend/.env    # fill in Razorpay/AWS credentials as you get them
make up                                  # docker compose: postgres+pgvector, pgadmin, redis, backend
make migrate                             # alembic upgrade head
```

API docs (when `DEBUG=true`): http://localhost:8000/docs
Health check: http://localhost:8000/health

pgAdmin: http://localhost:5050 (login with `PGADMIN_EMAIL`/`PGADMIN_PASSWORD` from `.env`,
default `admin@purelioraa.com` / `admin`). Add a new server there with:
- Host: `postgres` (the compose service name — not `localhost`)
- Port: `5432`
- Username/password/database: whatever you set in `.env` (`POSTGRES_USER`/`POSTGRES_PASSWORD`/`POSTGRES_DB`, default `postgres`/`postgres`/`ecommerce`)

## Common commands

| Command | Description |
|---|---|
| `make up` | Build and start postgres, pgadmin, redis, backend |
| `make down` | Stop all services |
| `make logs` | Tail backend logs |
| `make migrate` | Apply Alembic migrations |
| `make revision m="add coupons table"` | Autogenerate a new migration |
| `make test` | Run the backend test suite |
| `make lint` | Ruff + mypy |
| `make format` | Ruff format |

## Repository layout

```
ecommerce-platform/
├── backend/            FastAPI service — see backend/README-equivalent in docs/ARCHITECTURE.md
├── docs/
│   └── ARCHITECTURE.md Full architecture writeup
├── docker-compose.yml   postgres+pgvector, redis, backend
├── Makefile
└── .github/workflows/  CI (lint, migrate, test)
```
