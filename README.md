# Glow & Grace — Beauty Parlor Website

A full-stack luxury beauty salon booking platform built with FastAPI, PostgreSQL, and vanilla HTML/Tailwind CSS.

---

## Branches

This repository has two branches. Pick the one you want to run:

| Branch   | Description                                              | README                                    |
|----------|----------------------------------------------------------|-------------------------------------------|
| `master` | Original version — single page, no auth, anonymous users | [README-master.md](./README-master.md)   |
| `main`   | Latest version — separate admin portal, JWT auth, phone-based user identity, configurable API URL | [README-main.md](./README-main.md) |

---

## Quick Reference

### `master` branch
- Everything in one `index.html` — client view + manager dashboard
- No login required for anything
- Simple setup, good for understanding the base architecture

### `main` branch
- `index.html` — client-only SPA, phone-gated booking and My Bookings
- `admin.html` — separate manager portal with JWT login
- `config.js` — configurable frontend API URL (works locally and in production)
- Full user identity system with `users` table

---

> For technical decisions, architecture explanations, and interview prep — see [DEVELOPER-GUIDE.md](./DEVELOPER-GUIDE.md)
