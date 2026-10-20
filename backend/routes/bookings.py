import random
import string
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import get_db
from models import Booking, BookingStatus, User
from schemas import BookingCreate, BookingOut, BookingStatusUpdate
from auth import verify_admin_token

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])


def generate_ref_id() -> str:
    return "GLOW-" + "".join(random.choices(string.digits, k=4))


# ── Public: client books an appointment ──────────────────────────

@router.post("/", response_model=BookingOut, status_code=201)
async def create_booking(payload: BookingCreate, db: AsyncSession = Depends(get_db)):
    # Look up user by phone
    result = await db.execute(select(User).where(User.phone == payload.phone))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please identify first.")

    ref_id = generate_ref_id()
    while True:
        existing = await db.execute(select(Booking).where(Booking.ref_id == ref_id))
        if not existing.scalar_one_or_none():
            break
        ref_id = generate_ref_id()

    booking = Booking(
        ref_id=ref_id,
        user_id=user.id,
        client_name=user.name,
        client_email=user.email,
        client_phone=user.phone,
        service_title=payload.service_title,
        price=payload.price,
        stylist_name=payload.stylist_name,
        date=payload.date,
        time_slot=payload.time_slot,
        notes=payload.notes,
        status=BookingStatus.confirmed,
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return booking


# ── Public: client looks up their own bookings by phone ──────────

@router.get("/mine", response_model=List[BookingOut])
async def get_my_bookings(phone: str = Query(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Booking)
        .where(Booking.client_phone == phone)
        .order_by(Booking.created_at.desc())
    )
    return result.scalars().all()


# ── Admin: all bookings (protected) ──────────────────────────────

@router.get("/", response_model=List[BookingOut], dependencies=[Depends(verify_admin_token)])
async def get_all_bookings(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Booking).order_by(Booking.created_at.desc())
    if status and status != "ALL":
        stmt = stmt.where(Booking.status == status)
    result = await db.execute(stmt)
    return result.scalars().all()


# ── Admin: stats (protected) ─────────────────────────────────────

@router.get("/stats", dependencies=[Depends(verify_admin_token)])
async def get_stats(db: AsyncSession = Depends(get_db)):
    total = (await db.execute(select(func.count()).select_from(Booking))).scalar()
    revenue = (await db.execute(
        select(func.sum(Booking.price)).where(Booking.status != BookingStatus.cancelled)
    )).scalar() or 0
    pending = (await db.execute(
        select(func.count()).select_from(Booking).where(Booking.status == BookingStatus.pending)
    )).scalar()
    top_row = (await db.execute(
        select(Booking.service_title, func.count().label("cnt"))
        .group_by(Booking.service_title)
        .order_by(func.count().desc())
        .limit(1)
    )).first()
    total_users = (await db.execute(select(func.count()).select_from(User))).scalar()

    return {
        "total_bookings": total,
        "revenue": revenue,
        "pending": pending,
        "top_service": top_row[0] if top_row else "N/A",
        "total_users": total_users,
    }


# ── Admin: update status (protected) ─────────────────────────────

@router.patch("/{ref_id}/status", response_model=BookingOut, dependencies=[Depends(verify_admin_token)])
async def update_booking_status(
    ref_id: str, payload: BookingStatusUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Booking).where(Booking.ref_id == ref_id))
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking {ref_id} not found")
    booking.status = payload.status
    await db.commit()
    await db.refresh(booking)
    return booking


# ── Admin: delete booking (protected) ────────────────────────────

@router.delete("/{ref_id}", dependencies=[Depends(verify_admin_token)])
async def delete_booking(ref_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Booking).where(Booking.ref_id == ref_id))
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking {ref_id} not found")
    await db.delete(booking)
    await db.commit()
    return {"success": True, "message": f"Booking {ref_id} deleted"}
