from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import User
from schemas import UserIdentify, UserOut

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post("/identify", response_model=UserOut)
async def identify_user(payload: UserIdentify, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == payload.phone))
    user = result.scalar_one_or_none()

    if user:
        # Returning user — update name/email if provided
        if payload.name and not user.name:
            user.name = payload.name
        if payload.email and not user.email:
            user.email = payload.email
        await db.commit()
        await db.refresh(user)
        return user

    # New user — name is required
    if not payload.name:
        raise HTTPException(status_code=400, detail="Name is required for new users")

    user = User(phone=payload.phone, name=payload.name, email=payload.email)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
