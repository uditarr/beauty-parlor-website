# Glow & Grace — Master Branch (v1)

This is the original version of the project — a single-page full-stack beauty salon app. Everything lives in one `index.html` with the client view, manager dashboard, and backend code tab all together.

> For the latest version with admin portal, phone-based identity, and JWT auth — see the `main` branch and `README-main.md`.

---

## What's in This Version

- Single `index.html` — client booking page + manager dashboard + API tester tab all in one
- FastAPI backend with basic booking/service/review CRUD
- PostgreSQL database via Docker
- No authentication — anyone can access the manager dashboard
- No user identity — bookings are anonymous

---

## Tech Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Frontend  | HTML, Tailwind CSS, Vanilla JS      |
| Backend   | Python 3.9+, FastAPI, Uvicorn       |
| Database  | PostgreSQL 16 (via Docker)          |
| ORM       | SQLAlchemy 2 (async) + asyncpg      |
| Schemas   | Pydantic v2                         |

---

## Project Structure

```
beauty-parlor-website/
├── index.html              # Full SPA — client + admin + API tester in one file
├── docker-compose.yml      # PostgreSQL container setup
├── .env                    # Environment variables (git-ignored)
└── backend/
    ├── main.py             # FastAPI app entry point
    ├── database.py         # Async SQLAlchemy engine + session
    ├── models.py           # ORM models: Booking, Service, Review
    ├── schemas.py          # Pydantic request/response schemas
    ├── seed.py             # Seeds demo data into the database
    ├── requirements.txt    # Python dependencies
    └── routes/
        ├── bookings.py     # Booking CRUD + stats endpoints
        ├── services.py     # Services CRUD endpoints
        └── reviews.py      # Reviews endpoints
```

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Python 3.9 or higher (`python3` on macOS/Linux)
- pip3 (`pip3` on macOS/Linux)

---

## Setup & Run

```bash
# 1. Start PostgreSQL (port 5433)
docker-compose up -d

# 2. Create .env at project root
echo "DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5433/beauty_parlor" > .env

# 3. Install dependencies
cd backend
pip3 install -r requirements.txt

# 4. Seed demo data
python3 seed.py

# 5. Start API server
python3 -m uvicorn main:app --reload --port 8000
```

Then open `index.html` in your browser:

```bash
open ../index.html        # macOS
start ../index.html       # Windows
```

Or serve with Python:

```bash
cd ..
python3 -m http.server 3000
# open http://localhost:3000
```

---

## API Endpoints

| Method   | Endpoint                          | Description                     |
|----------|-----------------------------------|---------------------------------|
| `GET`    | `/api/bookings`                   | List all bookings               |
| `GET`    | `/api/bookings/stats`             | Dashboard stats                 |
| `POST`   | `/api/bookings`                   | Create a new booking            |
| `PATCH`  | `/api/bookings/{ref_id}/status`   | Update booking status           |
| `DELETE` | `/api/bookings/{ref_id}`          | Delete a booking                |
| `GET`    | `/api/services`                   | List all services               |
| `POST`   | `/api/services`                   | Add a new service               |
| `DELETE` | `/api/services/{id}`              | Delete a service                |
| `GET`    | `/api/reviews`                    | List all reviews                |
| `POST`   | `/api/reviews`                    | Submit a new review             |

---

## Reset Database

```bash
docker-compose down -v
docker-compose up -d
python3 seed.py
```
