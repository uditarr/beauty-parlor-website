from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Enum as SAEnum
from sqlalchemy.sql import func
import enum
from database import Base


class BookingStatus(str, enum.Enum):
    confirmed = "Confirmed"
    pending = "Pending"
    completed = "Completed"
    cancelled = "Cancelled"


class ServiceCategory(str, enum.Enum):
    hair = "hair"
    skin = "skin"
    nails = "nails"
    bridal = "bridal"


class Booking(Base):
    __tablename__ = "bookings"

    ref_id = Column(String, primary_key=True, index=True)
    client_name = Column(String, nullable=False)
    client_email = Column(String, nullable=False)
    client_phone = Column(String, nullable=False)
    service_title = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stylist_name = Column(String, nullable=False)
    date = Column(String, nullable=False)
    time_slot = Column(String, nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(SAEnum(BookingStatus), default=BookingStatus.confirmed, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Service(Base):
    __tablename__ = "services"

    id = Column(String, primary_key=True, index=True)
    category = Column(SAEnum(ServiceCategory), nullable=False)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    duration = Column(String, nullable=False)
    desc = Column(Text, nullable=False)
    img = Column(String, nullable=False)


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
