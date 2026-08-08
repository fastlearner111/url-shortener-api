
# URL Shortener API

<p>
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=flat&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-15%2B-4169E1?style=flat&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Redis-Cache-DC382D?style=flat&logo=redis&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=flat&logo=githubactions&logoColor=white" />
  <img src="https://img.shields.io/badge/Hosting-Render-F1502F?style=flat&logo=render&logoColor=white" />
</p>

🚀 URL Shortener API
A URL shortener REST API built with FastAPI, PostgreSQL, and Redis, using a clean layered architecture (routers, services, repositories, core, middleware). Includes JWT-secured link ownership, cache-aside redirects with hit/miss telemetry, fixed-window rate limiting with fail-open behavior, and load testing via Locust.

________________________________________

🌐 Live Cloud Deployment
•	Base API URL: https://url-shortener-api-6g12.onrender.com
•	Interactive Swagger UI Docs: https://url-shortener-api-6g12.onrender.com/docs
•	ReDoc Specification: https://url-shortener-api-6g12.onrender.com/redoc

________________________________________
```
✨ Core Features & Metrics
•	Tests: 15/15 passing
•	JWT-Enforced Link Ownership: /shorten requires a valid bearer token; links are attributed to the authenticated user (owner_id), not hardcoded.
•	Cache-Aside Redirects: Redirect lookups check Redis first, fall back to PostgreSQL on miss, then populate the cache — with hit/miss counters tracked in Redis.
•	Cache Invalidation on Update/Delete: Updating or deleting a short URL evicts its Redis key so redirects never serve stale data.
•	Fixed-Window Rate Limiting: IP-based request throttling with a fixed time window; fails open (bypasses limiting, doesn’t crash) if Redis is unreachable.
•	Request Timing: X-Process-Time header injected on every response via custom middleware.
•	Link Expiration: Expired links return 410 Gone.
•	Load Testing Ready: Includes a locustfile.py for concurrency/throughput testing.
```
________________________________________
```
🛠️ Tech Stack
•	Framework: FastAPI (Python 3.11+)
•	Database & ORM: PostgreSQL (Supabase) + SQLAlchemy ORM
•	Caching: Redis
•	Migrations: Alembic
•	Security: Passlib (bcrypt), Python-JOSE (JWT)
•	Performance Testing: Locust
•	Containerization: Docker & Docker Compose
•	Testing: Pytest
•	CI/CD: GitHub Actions
•	Hosting: Render
```
________________________________________
📁 Project Structure
``` url_shortener_api/
├── .github/workflows/
│   └── ci.yml                # GitHub Actions CI/CD pipeline
├── alembic/                  # Database migration scripts & versions
├── app/
│   ├── core/                 # App configs, DB engine, Redis, security & logging middleware
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── logging_middleware.py
│   │   ├── redis.py
│   │   └── security.py
│   ├── middleware/           # Custom HTTP & error handling middlewares
│   │   ├── errors.py
│   │   ├── ratelimit.py
│   │   ├── timing.py
│   │   └── logging.py
│   ├── models/               # SQLAlchemy database models
│   │   ├── models.py
│   │   └── url.py
│   ├── repositories/         # Database abstraction layer (CRUD operations)
│   │   └── crud.py
│   ├── routers/              # API endpoint route controllers
│   │   ├── auth.py
│   │   ├── health.py
│   │   ├── redirect.py
│   │   └── urls.py
│   ├── schemas/              # Pydantic request/response validation schemas
│   │   └── schemas.py
│   ├── services/             # Business logic layer
│   │   ├── analytics.py
│   │   ├── shortener.py
│   │   └── url_service.py
│   └── main.py               # Application entrypoint
├── tests/                    # Pytest test suite
│   ├── conftest.py
│   ├── test_analytics.py
│   ├── test_auth.py
│   ├── test_cache_metrics.py
│   ├── test_expiration.py
│   ├── test_main.py
│   └── test_redirect.py
├── docker-compose.yml        # Local multi-container stack configuration
├── Dockerfile                # Production container recipe
├── locustfile.py             # Locust load testing script
├── alembic.ini               # Alembic configuration
└── requirements.txt          # Python package dependencies 
```
_______________________________________
🔄 Cache-Aside Redirect Flow
```
Client          FastAPI           Redis           PostgreSQL
  |  GET /{code}    |               |                 |
  |---------------->|               |                 |
  |                 |--- GET code ->|                 |
  |                 |               |                 |
  |                 |  [Cache HIT]  |                 |
  |                 |<-- target_url-|                 |
  |<-- 307 Redirect-|               |                 |
  |                 |               |                 |
  |                 |  [Cache MISS] |                 |
  |                 |<---- nil -----|                 |
  |                 |---------------------- SELECT -->|
  |                 |<--------------------- target_url|
  |                 |--- SET code ->|                 |
  |<-- 307 Redirect-|               |                 |
```
```
On update/delete: FastAPI --- DEL code ---> Redis  (evicts stale entry)

  On update/delete: FastAPI --- DEL code ---> Redis  (evicts stale entry)
The redirect path checks Redis before ever touching PostgreSQL, so hot links are served without a database round-trip. On a miss, the result is written back to Redis so the next request for that code is a cache hit. Updates and deletes explicitly evict the key so a stale cache entry can never outlive the source of truth in Postgres.
```
________________________________________
```
🔌 API Request / Response Examples
1. Shorten a URL (POST /urls/) — requires auth
Request:
curl -X POST 'https://url-shortener-api-6g12.onrender.com/urls/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <your_jwt_token>' \
  -H 'Content-Type: application/json' \
  -d '{"target_url": "https://www.example.com/very/long/path/to/resource"}'
Response (201 Created):
{
  "id": 1,
  "target_url": "https://www.example.com/very/long/path/to/resource",
  "short_code": "a8B3k9",
  "clicks": 0,
  "is_active": true,
  "created_at": "2026-08-07T22:00:00.000Z"
}
No token → 401 Unauthorized.

2. Redirect to Target URL (GET /{short_code})
Request:
curl -I https://url-shortener-api-6g12.onrender.com/a8B3k9
Response (307 Temporary Redirect):
HTTP/1.1 307 Temporary Redirect
location: https://www.example.com/very/long/path/to/resource
3. Expired Link
Response (410 Gone):
{
  "detail": "URL expired"
}
4. Rate Limit Exceeded
Response (429 Too Many Requests):
{
  "detail": "Rate limit exceeded: 10 per 1 minute"
}
```
________________________________________
```
🏛️ Design Decisions & Trade-Offs
Short code generation & collisions. Codes are generated as random Base62 strings ([a-zA-Z0-9]). The repository layer checks uniqueness against the database, and the service loops to regenerate on collision — simple and sufficient at current volumes, though a counter-based scheme would scale better at very high write throughput.

Caching: cache-aside over write-through. Redirects are the highest-throughput path, so GET /{code} checks Redis first, falls back to PostgreSQL on a miss, then populates the cache — avoiding a DB hit on every redirect (see diagram above). Hit/miss counts are tracked as Redis counters for basic cache-efficiency visibility. Update and delete operations explicitly evict the key (DEL) so a stale cache entry can never outlive the source of truth.

Rate limiting: fixed window, not sliding window. The limiter uses a fixed-window counter (SET key 1 EX window, then INCR) rather than a sliding-window log. This is simpler and cheaper than sliding-window/token-bucket approaches, with the known trade-off that burst traffic right at a window boundary can briefly exceed the intended rate — an acceptable trade-off for this project’s scale, but something a production system at higher traffic would want to revisit. If Redis itself is unreachable, the middleware fails open (bypasses limiting) rather than taking the API down.


Auth: JWT ownership on write paths. /shorten requires a valid bearer token and attributes the created link to the authenticated user rather than a hardcoded owner — this was a real bug caught during review (it originally defaulted every link to owner_id=1 with no auth check) and fixed by wiring Depends(get_current_user) into the endpoint.
```
________________________________________
```
🚀 Getting Started Locally
Prerequisites
•	Docker & Docker Compose
•	Git


1. Clone the Repository
```bash
git clone https://github.com/fastlearner111/url-shortener-api.git
cd url-shortener-api


2. Create a .env File
Copy .env.example to .env and fill in your own values:
DATABASE_URL=postgresql://postgres:your_password@db:5432/postgres
SECRET_KEY=your_super_secret_key_here
REDIS_URL=redis://redis:6379
SENTRY_DSN=your_sentry_dsn_here
ACCESS_TOKEN_EXPIRE_MINUTES=60


3. Run with Docker Compose
docker compose up --build
The API will be available locally at http://localhost:8000.


4. Apply Database Migrations
docker compose exec api alembic upgrade head
```

________________________________________
```
🧪 Running Tests & Load Tests
Run the automated test suite:
docker compose exec api pytest -v
Run load tests:
locust -f locustfile.py --host=http://localhost:8000
```
________________________________________
```
🔮 Future Improvements
•	Custom Aliases: Allow users to specify personalized short codes (e.g., /github, /portfolio).
•	Per-User Analytics Dashboard: Aggregate click data by geography, user-agent, and referral source.
•	Sliding-Window Rate Limiting: Replace the current fixed-window limiter to eliminate boundary-burst behavior at higher traffic.
•	Refresh Tokens: Extend the current JWT flow with refresh-token support for longer-lived sessions.
•	Load Test Benchmarks: Publish real Locust throughput/latency numbers (RPS, P95 latency, failure rate) once a representative benchmark run is completed.
```
