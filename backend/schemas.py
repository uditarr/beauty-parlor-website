from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models import BookingStatus, ServiceCategory


# ── Booking Schemas ──────────────────────────────────────────────

class BookingCreate(BaseModel):
    client_name: str
    client_email: str
    client_phone: str
    service_title: str
    price: float
    stylist_name: str
    date: str
    time_slot: str
    notes: Optional[str] = None


class BookingStatusUpdate(BaseModel):
    status: BookingStatus


class BookingOut(BaseModel):
    ref_id: str
    client_name: str
    client_email: str
    client_phone: str
    service_title: str
    price: float
    stylist_name: str
    date: str
    time_slot: str
    notes: Optional[str] = None
    status: BookingStatus
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Service Schemas ──────────────────────────────────────────────

class ServiceCreate(BaseModel):
    category: ServiceCategory
    title: str
    price: float
    duration: str
    desc: str
    img: Optional[str] = "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=400&q=80"


class ServiceOut(BaseModel):
    id: str
    category: ServiceCategory
    title: str
    price: float
    duration: str
    desc: str
    img: str

    model_config = {"from_attributes": True}


# ── Review Schemas ───────────────────────────────────────────────

class ReviewCreate(BaseModel):
    name: str
    rating: int
    comment: str


class ReviewOut(BaseModel):
    id: int
    name: str
    rating: int
    comment: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
