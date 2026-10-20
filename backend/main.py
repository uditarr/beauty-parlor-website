from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routes import bookings, services, reviews, auth, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Glow & Grace Beauty Lounge API",
    description="REST API for the Glow & Grace beauty parlor.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(bookings.router)
app.include_router(services.router)
app.include_router(reviews.router)


@app.get("/")
async def root():
    return {"message": "Glow & Grace Beauty Lounge REST API v2 — Active", "docs": "/docs"}
