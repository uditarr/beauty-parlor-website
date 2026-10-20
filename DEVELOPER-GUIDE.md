# Glow & Grace — Developer Guide & Interview Reference

This document explains every technical decision made in this project — what we built, why we chose each technology, and how each feature works under the hood. Use this as a reference when discussing the project in interviews.

---

## Project Overview

Glow & Grace is a full-stack beauty salon booking platform. It has two separate user-facing pages:

- **`index.html`** — the client-facing SPA where visitors browse services, book appointments, and view their bookings
- **`admin.html`** — a protected manager dashboard for the salon owner to manage bookings and services

The backend is a REST API built with Python and FastAPI, backed by a PostgreSQL database.

---

## Technology Choices & Why

### Python + FastAPI (Backend)

**What:** FastAPI is a modern Python web framework for building REST APIs.

**Why we chose it:**
- **Async by default** — FastAPI is built on `asyncio`, which means it can handle many concurrent requests without blocking (important for a booking system that might get simultaneous requests)
- **Auto-generated docs** — FastAPI automatically generates Swagger UI at `/docs` with zero extra work, which is great for testing and sharing the API
- **Pydantic integration** — request/response validation is built in; if someone sends wrong data, FastAPI rejects it automatically with a clear error
- **Type hints** — Python type annotations make the code self-documenting and catch bugs early
- **Fast development** — less boilerplate than Django or Flask for REST APIs

**Interview answer:** *"We used FastAPI because it's async-first which gives better performance for I/O-bound operations like database queries, and it automatically validates request/response data using Pydantic schemas — so we don't have to write manual validation code."*

---

### PostgreSQL (Database)

**What:** PostgreSQL is an open-source relational database.

**Why we chose it:**
- **ACID compliance** — transactions are reliable; a booking either fully saves or fully fails, never half-saved
- **Relational data fits our model** — users have bookings, bookings reference services; foreign keys enforce data integrity
- **Production standard** — used by most serious applications, well-supported on all cloud providers
- **JSON support** — PostgreSQL can also store JSON if we ever need flexible data

**Why not MongoDB or SQLite:**
- SQLite is fine for local dev but not suitable for production with concurrent writes
- MongoDB is document-based and better for unstructured data; our data is clearly relational (user → bookings → services)

**Interview answer:** *"We chose PostgreSQL because our data is relational — users have bookings, bookings reference services — so a relational database with foreign key constraints fits naturally. PostgreSQL is also production-grade and ACID-compliant, meaning we never end up with partial or corrupt booking data."*

---

### SQLAlchemy 2.0 with asyncpg (ORM + Driver)

**What:** SQLAlchemy is a Python ORM (Object Relational Mapper). asyncpg is the async PostgreSQL driver.

**Why we chose it:**
- **ORM** means we write Python classes instead of raw SQL — the `Booking` class maps directly to the `bookings` table
- **Async support** — SQLAlchemy 2.0 supports `async/await` natively, so database queries don't block the event loop
- **asyncpg** is the fastest async PostgreSQL driver for Python
- **Migration-friendly** — SQLAlchemy can create/alter tables programmatically

**Key concept — async sessions:**
```python
async with AsyncSessionLocal() as session:
    result = await session.execute(select(Booking))
    bookings = result.scalars().all()
```
The `await` means the server can handle other requests while waiting for the database to respond.

**Interview answer:** *"We used SQLAlchemy with async sessions and the asyncpg driver. This means every database query is non-blocking — while one request waits for the database, the server can process other incoming requests. This is the difference between sync and async I/O."*

---

### Pydantic v2 (Data Validation)

**What:** Pydantic is a Python library for data validation using type hints.

**Why we chose it:**
- **Automatic validation** — if a client sends `price: "hello"` instead of a number, Pydantic rejects it before it reaches our code
- **Serialization** — converts database ORM objects into clean JSON responses automatically
- **`from_attributes = True`** — allows Pydantic to read data from SQLAlchemy model instances directly
- **Clear schemas** — `BookingCreate`, `BookingOut`, `UserOut` etc. document exactly what data flows in and out of each endpoint

**Interview answer:** *"Pydantic acts as a contract for our API. Every endpoint declares what it accepts and what it returns using schema classes. If the input doesn't match the schema, FastAPI returns a 422 error automatically — no manual validation code needed."*

---

### JWT (JSON Web Tokens) for Admin Auth

**What:** JWT is a standard for stateless authentication tokens.

**Why we chose it:**
- **Stateless** — the server doesn't need to store sessions in a database; the token itself contains the user's identity and role
- **Admin-only auth** — clients don't need passwords; only the salon manager needs to log in
- **Simple to implement** — `python-jose` library handles encoding/decoding
- **Secure** — tokens are signed with a secret key; tampering is detectable

**How it works in our app:**
1. Admin POSTs username/password to `/login`
2. Server verifies credentials against `.env` values
3. Server returns a signed JWT token containing `{ "role": "admin", "exp": ... }`
4. Admin stores token in `localStorage`
5. Every admin API call sends `Authorization: Bearer <token>` header
6. `verify_admin_token` dependency decodes and validates the token on each request

**Why not sessions/cookies:**
- Sessions require server-side storage (database or Redis)
- JWTs are self-contained — easier to scale horizontally
- For a single admin user, JWT is simpler and sufficient

**Interview answer:** *"We used JWT for admin authentication. The token is stateless — it contains the role claim signed with a secret. The server doesn't store any session data; it just verifies the signature on every request. This is more scalable than server-side sessions."*

---

### Phone-Based User Identity (No Password for Clients)

**What:** Instead of asking clients to register with email/password, we identify them by phone number.

**Why this design:**
- **Lower friction** — most salon clients just want to book; a full registration form increases drop-off
- **Realistic** — salons already collect phone numbers for appointment reminders
- **Still persistent** — bookings are linked to a user record in the database, so "My Bookings" works
- **sessionStorage** — the phone/name is stored in the browser's session storage, so users don't re-enter it on every page visit (but it clears when they close the tab — appropriate privacy for a shared device)

**How it works:**
1. User enters phone → `POST /api/users/identify`
2. If phone exists in DB → returns existing user (no name needed)
3. If phone is new → returns 400 "Name is required" → frontend shows name form
4. New user created → stored in `users` table → linked to future bookings

**Interview answer:** *"We avoided password-based auth for clients to reduce friction. Phone number acts as the identity — it's something salon clients already share. We use a `users` table with a unique phone index, and bookings are foreign-keyed to users. This gives us personalization (My Bookings) without requiring a full account system."*

---

### Vanilla JS + Tailwind CSS (Frontend)

**What:** No JavaScript framework — just plain HTML, CSS (via Tailwind), and vanilla JS with `fetch()`.

**Why not React/Vue/Angular:**
- **Simplicity** — for a single-page app with a few sections, a framework adds unnecessary complexity and build tooling
- **No build step** — open the HTML file directly in a browser, it works
- **Tailwind CDN** — utility-first CSS via CDN means no npm, no webpack, no bundler
- **Faster to build** — all logic is in one file, easy to read and modify

**Why Tailwind:**
- Utility classes like `bg-roseGold-500`, `rounded-3xl`, `glass-card` make styling fast
- No context switching between HTML and CSS files
- Custom theme defined once in `tailwind.config` — consistent colors everywhere

**Interview answer:** *"We chose vanilla JS deliberately. The app is a multi-section single page — there's no complex state management that would justify React. Using fetch() directly keeps it simple, and Tailwind CSS handles all styling with utility classes so there's no separate stylesheet to maintain."*

---

### Docker + Docker Compose (Database)

**What:** Docker runs the PostgreSQL database in an isolated container.

**Why:**
- **No local installation needed** — developers don't need to install and configure PostgreSQL locally
- **Reproducible** — everyone runs the exact same database version (PostgreSQL 16 Alpine)
- **Port isolation** — we mapped to port 5433 instead of 5432 to avoid conflicts with any locally installed Postgres
- **Named volumes** — data persists between container restarts with `postgres_data` volume
- **One command** — `docker-compose up -d` and the database is ready

**Interview answer:** *"We containerized the database with Docker so any developer can run the project without installing PostgreSQL locally. The `docker-compose.yml` defines the exact version, credentials, and port mapping — `docker-compose up -d` is all it takes."*

---

## Architecture Decisions

### Why Separate `index.html` and `admin.html`?

- **Security** — the admin dashboard is a completely separate page; there's no way a client accidentally accesses admin routes
- **Separation of concerns** — client UX and admin UX are very different; keeping them in separate files makes both cleaner
- **Different auth** — clients use phone identity (sessionStorage), admins use JWT (localStorage)
- **Simpler code** — each page only loads what it needs

### Why `sessionStorage` for Clients and `localStorage` for Admins?

- **`sessionStorage`** clears when the browser tab closes — appropriate for a client on a shared salon device
- **`localStorage`** persists across browser sessions — appropriate for the manager who wants to stay logged in

### Why `.env` File for Configuration?

- Secrets (DB password, JWT secret, admin credentials) must never be hardcoded in source code
- `.env` is listed in `.gitignore` so it's never committed to git
- `pydantic-settings` reads the `.env` file and maps values to typed Python settings — if a required variable is missing, the app fails at startup with a clear error

### Why a Separate `seed.py`?

- Separates initial data setup from application code
- Can be run independently to reset demo data
- Skips tables that already have data — safe to run multiple times

---

## Data Models

### `users` table
| Column     | Type      | Notes                          |
|------------|-----------|--------------------------------|
| id         | Integer   | Auto-increment primary key     |
| phone      | String    | Unique, indexed — identity key |
| name       | String    | Required                       |
| email      | String    | Optional                       |
| created_at | DateTime  | Auto server timestamp          |

### `bookings` table
| Column        | Type    | Notes                              |
|---------------|---------|------------------------------------|
| ref_id        | String  | Primary key, e.g. `GLOW-1001`      |
| user_id       | Integer | Foreign key → users.id             |
| client_name   | String  | Denormalized for quick display     |
| client_phone  | String  | Denormalized for quick lookup      |
| service_title | String  | Name of the booked service         |
| price         | Float   |                                    |
| stylist_name  | String  |                                    |
| date          | String  | YYYY-MM-DD                         |
| time_slot     | String  | e.g. "10:00 AM"                    |
| status        | Enum    | Pending / Confirmed / Cancelled / Completed |
| created_at    | DateTime| Auto server timestamp              |

### `services` table
| Column   | Type   | Notes                              |
|----------|--------|------------------------------------|
| id       | String | e.g. `srv-1`                       |
| category | Enum   | hair / skin / nails / bridal       |
| title    | String |                                    |
| price    | Float  |                                    |
| duration | String | e.g. "75 mins"                     |
| desc     | String |                                    |
| img      | String | Unsplash image URL                 |

---

## API Design Decisions

### Why `/api/users/identify` instead of `/api/users/login`?

The word "identify" is more accurate — we're not authenticating (no password), we're identifying who the user is. If they exist, we return their record. If not, we create them. It's a single endpoint that handles both cases (upsert-like behavior).

### Why denormalize `client_name` and `client_phone` on bookings?

Even though `user_id` is a foreign key, we also store `client_name` and `client_phone` directly on the booking. This is intentional:
- If a user record is deleted, booking history is preserved
- Admin can see client details on the bookings table without joining to the users table
- Simpler queries for the admin dashboard

### Why `GET /api/bookings/mine?phone=...` instead of using a JWT?

Clients don't have JWTs — they identify by phone. The phone is already stored in `sessionStorage`. Passing it as a query parameter is simple and sufficient. For a production app, you'd add rate limiting to this endpoint to prevent enumeration attacks.

---

## Security Considerations

| Area                    | What we did                                  | Production improvement               |
|-------------------------|----------------------------------------------|---------------------------------------|
| Admin auth              | JWT with role claim                          | Add refresh tokens                    |
| Client identity         | Phone number, no password                    | Add OTP verification via SMS          |
| Secrets                 | `.env` file, git-ignored                     | Use secrets manager (AWS Secrets Mgr) |
| CORS                    | `allow_origins=["*"]` for development        | Restrict to actual frontend domain    |
| SQL injection           | SQLAlchemy ORM — parameterized queries only  | Already safe                          |
| JWT secret              | Hardcoded default in `.env`                  | Rotate regularly in production        |
| Admin password          | Plain text in `.env`                         | Hash with bcrypt in production        |

---

## Common Interview Questions

**Q: How does the booking flow work end to end?**

1. User enters phone → identified/created in `users` table → stored in `sessionStorage`
2. User picks service, stylist, date, time in the wizard
3. On submit: `POST /api/bookings` with `{ phone, service_title, price, stylist_name, date, time_slot }`
4. Backend looks up user by phone → creates booking with `user_id` FK → returns booking with `ref_id`
5. Frontend shows confirmation toast, navigates to My Bookings

**Q: How is the admin dashboard secured?**

Admin posts username/password to `/login`. Server checks against `.env` values. If valid, returns a JWT signed with `JWT_SECRET`. Every subsequent admin API call sends `Authorization: Bearer <token>`. The `verify_admin_token` FastAPI dependency decodes the token on each request — if the signature is invalid or the role isn't `admin`, it returns 401/403.

**Q: What happens if the same phone number is used twice?**

The `phone` column has a `UNIQUE` constraint in the database. The `identify` endpoint does a `SELECT` first — if the user exists, it returns their existing record without creating a duplicate. This is handled at the application layer before hitting the DB constraint.

**Q: Why is the database on port 5433 instead of 5432?**

Many developers have PostgreSQL installed locally on the default port 5432. Mapping Docker's container port to 5433 on the host avoids a port conflict. The `.env` file specifies `localhost:5433` so the app connects to Docker, not the local installation.

**Q: What is async/await and why does it matter here?**

Synchronous code waits for each operation to complete before moving on. When a database query takes 50ms, a sync server is blocked — it can't handle any other requests. With async/await, the server can handle hundreds of other requests during that 50ms wait. FastAPI and SQLAlchemy 2.0 are both async, so every database query uses `await` — the event loop is never blocked.

**Q: How would you scale this for production?**

- Move to a cloud database (AWS RDS, Supabase)
- Add authentication to the client side (OTP via SMS for phone verification)
- Add a CDN for static assets
- Deploy the FastAPI app behind a load balancer (multiple uvicorn workers)
- Replace CORS `allow_origins=["*"]` with the actual domain
- Add logging and monitoring (Sentry, Datadog)
- Add rate limiting to prevent abuse of the booking endpoint
