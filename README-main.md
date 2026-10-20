# Glow & Grace — Main Branch (v2)

This branch restructures the app into a clean client/admin separation with phone-based user identity and JWT-protected admin portal.

---

## What Changed from `master`

| Feature                        | master branch          | main branch                          |
|--------------------------------|------------------------|--------------------------------------|
| Manager dashboard              | Embedded in index.html | Separate `admin.html` with JWT login |
| Backend Code / API tab         | Visible to all users   | Removed from client page             |
| User identity                  | Anonymous              | Phone-number gate on load            |
| My Bookings                    | Shows all bookings     | Shows only the logged-in user's own  |
| Admin auth                     | None                   | Username/password → JWT token        |
| Users table                    | Not present            | New `users` table, bookings linked   |

---

## Architecture

```
beauty-parlor-website/
├── index.html        # Client SPA — phone-gated, personalized
├── admin.html        # Manager portal — separate JWT-protected page
├── docker-compose.yml
├── .env              # Secrets (not committed)
└── backend/
    ├── main.py
    ├── database.py
    ├── models.py         # User, Booking, Service, Review
    ├── schemas.py
    ├── auth.py           # JWT verify dependency
    ├── seed.py
    ├── requirements.txt
    └── routes/
        ├── auth.py       # POST /login
        ├── users.py      # POST /api/users/identify
        ├── bookings.py
        ├── services.py
        └── reviews.py
```

---

## Environment Variables (`.env`)

Create a `.env` file at the project root:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5433/beauty_parlor
JWT_SECRET=glowandgrace_super_secret_jwt_2026
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=480
ADMIN_USERNAME=admin
ADMIN_PASSWORD=glow2026
```

---

## Setup & Run

```bash
# 1. Start PostgreSQL (port 5433)
docker-compose up -d

# 2. Install dependencies
cd backend
pip3 install -r requirements.txt

# 3. Seed demo data (users + bookings + services + reviews)
python3 seed.py

# 4. Start API server
python3 -m uvicorn main:app --reload --port 8000
```

Open pages:
```bash
open ../index.html    # Client page
open ../admin.html    # Admin portal
```

Or serve statically:
```bash
cd ..
python3 -m http.server 3000
# http://localhost:3000/index.html
# http://localhost:3000/admin.html
```

---

## Default Credentials

### Admin Portal (`admin.html`)
| Field    | Value      |
|----------|------------|
| Username | `admin`    |
| Password | `glow2026` |

### Demo Client Accounts (seeded)
| Name          | Phone        |
|---------------|--------------|
| Sophia Loren  | +1 555-0192  |
| Olivia Wilde  | +1 555-0193  |
| Emma Watson   | +1 555-0194  |

---

## API Endpoints

### Public
| Method | Endpoint                       | Description                         |
|--------|--------------------------------|-------------------------------------|
| POST   | `/api/users/identify`          | Get or create user by phone         |
| POST   | `/api/bookings`                | Create booking (send `phone` field) |
| GET    | `/api/bookings/mine?phone=...` | Current user's bookings only        |
| GET    | `/api/services`                | List all services                   |
| GET    | `/api/reviews`                 | List reviews                        |
| POST   | `/api/reviews`                 | Submit a review                     |

### Admin (JWT required)
| Method | Endpoint                        | Description            |
|--------|---------------------------------|------------------------|
| POST   | `/login`                        | Get JWT token          |
| GET    | `/api/bookings`                 | All bookings           |
| GET    | `/api/bookings/stats`           | Revenue, counts, users |
| PATCH  | `/api/bookings/{ref_id}/status` | Update status          |
| DELETE | `/api/bookings/{ref_id}`        | Delete booking         |
| POST   | `/api/services`                 | Add service            |
| DELETE | `/api/services/{id}`            | Delete service         |

---

## Testing

### Client Flow
1. Open `index.html` — phone gate appears on load.
2. Enter `+1 555-0192` → greeted as **Sophia Loren** (existing user).
3. Enter a new number → prompted to provide your name (new account created).
4. Use **Book Now** wizard — 3 steps: service → stylist/time → confirm.
5. **My Bookings** shows only your own appointments.
6. **Logout** clears session and returns to phone gate.

### Admin Flow
1. Open `admin.html` → login screen.
2. Enter `admin` / `glow2026` → dashboard loads.
3. Stats cards: revenue, bookings, pending count, total users, top service.
4. Bookings table: update status via dropdown, delete with trash icon.
5. Services table: delete entries, add new via **+ Add Service** modal.
6. **Logout** returns to login screen.

### API via curl
```bash
# Get admin token
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"glow2026"}'

# Use token for protected routes
curl http://localhost:8000/api/bookings \
  -H "Authorization: Bearer <token>"

# Identify a client by phone
curl -X POST http://localhost:8000/api/users/identify \
  -H "Content-Type: application/json" \
  -d '{"phone":"+1 555-0192"}'
```

API docs (Swagger): http://localhost:8000/docs

---

## Reset Database

```bash
docker-compose down -v
docker-compose up -d
python3 seed.py
```
