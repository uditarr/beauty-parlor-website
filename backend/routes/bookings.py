import random
import string
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import get_db
from models import Booking, BookingStatus
from schemas import BookingCreate, BookingOut, BookingStatusUpdate

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])


def generate_ref_id() -> str:
    return "GLOW-" + "".join(random.choices(string.digits, k=4))


@router.get("/", response_model=List[BookingOut])
async def get_all_bookings(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Booking).order_by(Booking.created_at.desc())
    if status and status != "ALL":
        stmt = stmt.where(Booking.status == status)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/lookup", response_model=List[BookingOut])
async def lookup_booking(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    q_lower = q.lower()
    stmt = select(Booking).where(
        Booking.ref_id.ilike(f"%{q_lower}%")
        | Booking.client_phone.ilike(f"%{q_lower}%")
        | Booking.client_email.ilike(f"%{q_lower}%")
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    total_stmt = await db.execute(select(func.count()).select_from(Booking))
    total = total_stmt.scalar()

    revenue_stmt = await db.execute(
        select(func.sum(Booking.price)).where(Booking.status != BookingStatus.cancelled)
    )
    revenue = revenue_stmt.scalar() or 0

    pending_stmt = await db.execute(
        select(func.count()).select_from(Booking).where(Booking.status == BookingStatus.pending)
    )
    pending = pending_stmt.scalar()

    top_stmt = await db.execute(
        select(Booking.service_title, func.count().label("cnt"))
        .group_by(Booking.service_title)
        .order_by(func.count().desc())
        .limit(1)
    )
    top_row = top_stmt.first()
    top_service = top_row[0] if top_row else "N/A"

    return {
        "total_bookings": total,
        "revenue": revenue,
        "pending": pending,
        "top_service": top_service,
    }


@router.post("/", response_model=BookingOut, status_code=201)
async def create_booking(payload: BookingCreate, db: AsyncSession = Depends(get_db)):
    ref_id = generate_ref_id()
    # Ensure uniqueness
    while True:
        existing = await db.execute(select(Booking).where(Booking.ref_id == ref_id))
        if not existing.scalar_one_or_none():
            break
        ref_id = generate_ref_id()

    booking = Booking(ref_id=ref_id, **payload.model_dump())
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return booking


@router.patch("/{ref_id}/status", response_model=BookingOut)
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


@router.delete("/{ref_id}")
async def delete_booking(ref_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Booking).where(Booking.ref_id == ref_id))
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking {ref_id} not found")
    await db.delete(booking)
    await db.commit()
    return {"success": True, "message": f"Booking {ref_id} deleted"}
