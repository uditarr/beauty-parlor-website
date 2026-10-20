from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import Review
from schemas import ReviewCreate, ReviewOut

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


@router.get("/", response_model=List[ReviewOut])
async def get_reviews(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Review).order_by(Review.created_at.desc()))
    return result.scalars().all()


@router.post("/", response_model=ReviewOut, status_code=201)
async def create_review(payload: ReviewCreate, db: AsyncSession = Depends(get_db)):
    review = Review(**payload.model_dump())
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review
