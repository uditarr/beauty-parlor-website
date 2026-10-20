# Glow & Grace — Beauty Parlor Website

A full-stack beauty salon booking platform with a **FastAPI + PostgreSQL** backend and a single-page HTML/Tailwind CSS frontend.

---

## Tech Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Frontend  | HTML, Tailwind CSS, Vanilla JS      |
| Backend   | Python 3.11+, FastAPI, Uvicorn      |
| Database  | PostgreSQL 16 (via Docker)          |
| ORM       | SQLAlchemy 2 (async) + asyncpg      |
| Schemas   | Pydantic v2                         |

---

## Project Structure

```
beauty-parlor-website/
├── index.html              # Frontend — client view, admin dashboard, API tester
├── docker-compose.yml      # PostgreSQL container setup
├── .env                    # Environment variables (DB connection string)
└── backend/
    ├── main.py             # FastAPI app entry point
    ├── database.py         # Async SQLAlchemy engine + session
    ├── models.py           # ORM models: Booking, Service, Review
    ├── schemas.py          # Pydantic request/response schemas
    ├── seed.py             # Seeds demo data into the database
    ├── requirements.txt    # Python dependencies
    └── routes/
        ├── bookings.py     # Booking CRUD + lookup + stats endpoints
        ├── services.py     # Services CRUD endpoints
        └── reviews.py      # Reviews CRUD endpoints
```

---

## Prerequisites

Make sure you have the following installed:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for PostgreSQL)
- Python 3.9 or higher (`python3` on macOS/Linux)
- pip3 (`pip3` on macOS/Linux)

---

## Step-by-Step Setup

### Step 1 — Start the PostgreSQL Database

Run the Docker container using the included `docker-compose.yml`:

```bash
docker-compose up -d
```

This starts a PostgreSQL 16 container with:
- **Host:** `localhost`
- **Port:** `5433` (mapped from container's 5432 — avoids conflict with any local Postgres)
- **Database:** `beauty_parlor`
- **Username:** `postgres`
- **Password:** `password`

To verify it is running:

```bash
docker-compose ps
```

To stop the database later:

```bash
docker-compose down
```

> Data is persisted in a Docker volume (`postgres_data`) — it survives container restarts.

---

### Step 2 — Configure Environment Variables

The `.env` file at the project root already contains the correct default connection string:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5433/beauty_parlor
```

If you change the Docker credentials, update this file to match.

---

### Step 3 — Install Python Dependencies

```bash
cd backend
pip3 install -r requirements.txt
```

---

### Step 4 — Seed Demo Data

This creates all database tables and inserts the initial services, bookings, and reviews:

```bash
python3 seed.py
```

You should see output like:

```
  Seeded 6 services.
  Seeded 3 bookings.
  Seeded 2 reviews.
Seed complete.
```

> Run `seed.py` only once. It skips seeding if data already exists.

---

### Step 5 — Start the FastAPI Server

```bash
python3 -m uvicorn main:app --reload --port 8000
```

The server starts at **http://localhost:8000**

Interactive API documentation is available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

### Step 6 — Open the Website

Open `index.html` directly in your browser:

```bash
open ../index.html        # macOS
start ../index.html       # Windows
xdg-open ../index.html    # Linux
```

Or serve it with any static file server, for example:

```bash
cd ..
python -m http.server 3000
# then open http://localhost:3000
```

---

## API Endpoints

| Method   | Endpoint                          | Description                     |
|----------|-----------------------------------|---------------------------------|
| `GET`    | `/api/bookings`                   | List all bookings (with filter) |
| `GET`    | `/api/bookings/stats`             | Dashboard stats (revenue, etc.) |
| `GET`    | `/api/bookings/lookup?q=...`      | Client booking lookup           |
| `POST`   | `/api/bookings`                   | Create a new booking            |
| `PATCH`  | `/api/bookings/{ref_id}/status`   | Update booking status           |
| `DELETE` | `/api/bookings/{ref_id}`          | Delete a booking                |
| `GET`    | `/api/services`                   | List all services               |
| `POST`   | `/api/services`                   | Add a new service               |
| `DELETE` | `/api/services/{id}`              | Delete a service                |
| `GET`    | `/api/reviews`                    | List all reviews                |
| `POST`   | `/api/reviews`                    | Submit a new review             |

---

## Features

- **Client View** — Browse services, book appointments via 4-step wizard, lookup bookings, submit reviews
- **Manager Dashboard** — View stats, manage all bookings, filter by status, update/delete entries, add services
- **Backend Code Tab** — View Python/FastAPI source code inline, test live API endpoints interactively
- **Persistent Storage** — All data saved to PostgreSQL via async SQLAlchemy ORM

---

## Resetting the Database

To wipe all data and start fresh:

```bash
docker-compose down -v      # removes the volume (all data)
docker-compose up -d        # starts a fresh PostgreSQL container
python3 seed.py             # re-seeds demo data
```
