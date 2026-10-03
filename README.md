# URL Shortener API

![CI](https://github.com/fastlearner111/url-shortener-api/actions/workflows/ci.yml/badge.svg)

<p>
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/GitHub%20Actions-2088FF?style=flat&logo=githubactions&logoColor=white" />
  <img src="https://img.shields.io/badge/Render-F1502F?style=flat&logo=render&logoColor=white" />
</p>

A REST API for creating and resolving short links, built with FastAPI, PostgreSQL, and Redis. Authenticated users create links and manage their own. Redirects are served through a Redis cache-aside layer.

**Live deployment**
- Base URL: https://url-shortener-api-6g12.onrender.com
- Swagger UI: https://url-shortener-api-6g12.onrender.com/docs
- ReDoc: https://url-shortener-api-6g12.onrender.com/redoc

Hosted on Render's free tier with a Supabase PostgreSQL database. After a period of inactivity the first request can be slow while the instance wakes up.

## What it does

- JWT bearer authentication (register and login), with bcrypt-hashed passwords
- Create short links with an optional expiry time
- Owner-only update and delete, enforced in the service layer (403 for anyone else)
- Redirects check Redis first and fall back to PostgreSQL on a miss; expired links return 410, unknown codes return 404
- Redis-backed fixed-window rate limiting per client IP that fails open if Redis is unreachable, verified against the deployed API and with Redis stopped locally
- `X-Process-Time` header on every response from a timing middleware

## Stack

Python 3.11, FastAPI, SQLAlchemy, PostgreSQL (Supabase in production, a Postgres container locally), Redis, Docker and Docker Compose, Pytest, Locust, GitHub Actions, Render. Passwords use passlib with bcrypt, tokens use python-jose.

## API

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/auth/register` | none | JSON body `{"email", "password"}` |
| POST | `/auth/login` | none | JSON body, returns `{"access_token", "token_type"}` |
| POST | `/urls/shorten` | bearer | Body `{"original_url", "expires_at"?}` |
| GET | `/{short_code}` | none | 307 redirect, 404 if unknown, 410 if expired |
| PUT | `/urls/{short_code}` | bearer, owner | 403 for non-owners |
| DELETE | `/urls/{short_code}` | bearer, owner | 403 for non-owners |

Login takes a JSON body, not an OAuth2 form, so the Authorize button in Swagger will not work. Call `POST /auth/login`, then send the token as `Authorization: Bearer <token>`.

**Shorten a URL**

```bash
curl -X POST 'https://url-shortener-api-6g12.onrender.com/urls/shorten' \
  -H 'Authorization: Bearer <your_jwt_token>' \
  -H 'Content-Type: application/json' \
  -d '{"original_url": "https://www.example.com"}'
```

Response (200):

```json
{
  "id": 2,
  "original_url": "https://www.example.com",
  "short_code": "2BaPR8",
  "owner_id": 6,
  "created_at": "2026-10-03T17:32:10.974312",
  "updated_at": "2026-10-03T17:32:10.974315",
  "expires_at": null
}
```

A request without a token returns 401.

**Rate limit exceeded** (429): `{"detail": "Too many requests. Slow down."}`

## Project structure

```
app/
  core/          config, database engine, Redis cache wrapper, JWT and password helpers, logging middleware
  middleware/    rate limiter, timing, error handling
  models/        SQLAlchemy models (users, url_mappings, analytics_clicks)
  repositories/  database access (crud.py)
  routers/       auth, health, redirect, urls
  schemas/       Pydantic request and response models
  services/      business logic (url_service.py)
  main.py        application entrypoint
tests/           Pytest suite
locustfile.py    Locust load test
docker-compose.yml, Dockerfile, pytest.ini
.github/workflows/ci.yml
```

## Cache-aside redirect flow

```
Client          FastAPI           Redis           PostgreSQL
  |  GET /{code}    |               |                 |
  |---------------->|               |                 |
  |                 |--- GET code ->|                 |
  |                 |  [Cache HIT]  |                 |
  |                 |<-- url -------|                 |
  |<-- 307 ---------|               |                 |
  |                 |  [Cache MISS] |                 |
  |                 |<---- nil -----|                 |
  |                 |---------------------- SELECT -->|
  |                 |<---------------------- url -----|
  |                 |--- SET code ->|                 |
  |<-- 307 ---------|               |                 |
On update or delete: FastAPI --- DEL code ---> Redis
```

## Design decisions

**Cache-aside, not write-through.** Redirects are the hottest path, so the app checks Redis first, queries PostgreSQL on a miss, and stores the result. Entries expire after one hour, or at the link's expiry time if it has one. Creating a link does not populate the cache, so the first redirect to any link is always a miss. Updates and deletes evict the key.

**Fixed-window rate limiting.** Each client IP gets a counter in Redis. The counter and its 60-second expiry are created in one atomic call (`SET key 0 EX 60 NX`), then incremented. The default limit is 10 requests per minute per IP, configurable with the `RATE_LIMIT` environment variable. A fixed window is simple and cheap, with the known trade-off that bursts at a window boundary can briefly exceed the limit. If Redis is unreachable the limiter lets requests through and logs a warning, so a cache outage does not take the API down (verified locally by stopping the Redis container). The client IP is read from `X-Forwarded-For` because Render sits behind a proxy. `/docs`, `/redoc`, `/openapi.json`, and `/health` are exempt.

**Short codes.** Random base62 strings, checked against the database for collisions. After five failed attempts the code length grows to 8.

**Auth.** Tokens carry the user id in the `sub` claim. Ownership is checked in the service layer, not only in the route.

## Testing

17 tests cover registration and login, protected routes, redirects, expiry, update and delete, owner-only access, and cache metrics. Run them with:

```bash
docker compose up -d --build
docker compose exec web pytest -v
```

CI runs the suite on every push and pull request to `main`.

Honest notes on what the suite does and does not do:
- Most tests mock the logged-in user so they can focus on other behavior. `tests/test_auth_flow.py` does not mock it: it logs in through the real endpoint and sends the real token to a protected route.
- Tests run against in-memory SQLite, not PostgreSQL.
- The rate limiter is bypassed during tests. It was verified by hand against the deployed API (ten requests succeed, the eleventh returns 429).
- Some assertions are weak. The analytics test only checks that fields exist.

## Load test results

Run locally with Locust: Docker Compose on a single laptop, the load generator and the app sharing the same CPU, 20 concurrent simulated users, 60 seconds, rate limit raised for the run. Each user registers, logs in, creates links, and redirects only to links it created.

| | Run 1 | Run 2 |
|---|---|---|
| Requests (failures) | 733 (0) | 801 (0) |
| Redirect on cache hit, median | 16 ms | 18 ms |
| Redirect on cache miss, median | 69 ms | 66 ms |

Cache misses also include a PostgreSQL lookup and a write, so the gap is not purely cache benefit. These are local numbers from a self-limiting script (users wait between requests), so they say nothing about capacity.

On the deployed API, the first redirect to a new link reported an `X-Process-Time` of about 310 ms and the next five about 4 ms.

To reproduce:

```powershell
# PowerShell, as run
$env:RATE_LIMIT = "100000"; docker compose up -d
locust -f locustfile.py --host=http://localhost:8000 --headless -u 20 -r 5 -t 60s
Remove-Item Env:RATE_LIMIT; docker compose up -d
```

Never set `RATE_LIMIT` that high on a real deployment.

## Bugs found and fixed

- **Rate limiter silently disabled in production.** It connected to `localhost` instead of the configured `REDIS_URL`, and a bare `except: pass` hid the failure, so every request went through. Fixed by using the configured Redis URL, creating the counter and its expiry atomically, and logging a warning when Redis is unreachable. Verified against the deployed API.
- **JWT claim-key mismatch.** Login wrote `user_id` into the token while the verifier read `sub`, so authenticated requests were rejected. The test suite stayed green because a fixture mocked authentication for every test. Fixed the key and added tests that send a real login token through the real verifier. The tests fail if the key is changed back.
- **Duplicate redirect route without an expiry check.** An older `/{code}` route redirected expired links with a 307 while `/r/{code}` correctly returned 410. Consolidated into one implementation, and verified on the deployed API that an expired link returns 410.
- **Missing cache `delete` method.** Update and delete called a method the cache wrapper did not have, so they would have failed after the database commit. No test touched those routes. Added the method and a test that runs both.

## Known limitations

- **Click analytics are not implemented.** The `analytics_clicks` table and `GET /urls/stats/{short_code}` exist, but nothing records clicks, so the count is always 0. Counting in Redis and flushing in batches would keep database writes off the hot path.
- **Redirects share the strict rate limit.** Ten requests per minute per IP suits writes and logins, not redirects. Redirects should get a separate, much higher limit.
- **The rate limiter trusts the first `X-Forwarded-For` entry**, which a client may be able to spoof. A production setup should trust only the proxy's own hop.
- **No test confirms that eviction removes a cached key.** The update and delete test only checks that the calls succeed.
- **Alembic migrations are verified but not used at deploy time.** They rebuild the schema from an empty PostgreSQL database with no drift from the models (`alembic check` is clean), but the app still creates tables at startup with `create_all`. Switching deploys to `alembic upgrade head`, after running `alembic stamp head` on the existing production database, is the remaining step.
- **`updated_at` also changes when a cache-miss redirect happens**, which blurs the meaning of the field. A separate `last_accessed_at` column would fix it.
- **HEAD requests to a short link return 405.**
- **Sentry is initialized when `SENTRY_DSN` is set** but has not been verified end to end.

## Running locally

Prerequisites: Docker and Docker Compose.

```bash
git clone https://github.com/fastlearner111/url-shortener-api.git
cd url-shortener-api
docker compose up --build
```

The API is available at http://localhost:8000 after about 15 seconds on first start, while PostgreSQL initializes. Compose starts the API (service `web`), PostgreSQL, and Redis, and sets `DATABASE_URL`, `REDIS_URL`, and `SECRET_KEY` for local development. Change the secret for anything beyond local use.