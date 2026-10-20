import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import Service
from schemas import ServiceCreate, ServiceOut

router = APIRouter(prefix="/api/services", tags=["Services"])


@router.get("/", response_model=List[ServiceOut])
async def get_services(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Service))
    return result.scalars().all()


@router.post("/", response_model=ServiceOut, status_code=201)
async def create_service(payload: ServiceCreate, db: AsyncSession = Depends(get_db)):
    service = Service(id=f"srv-{uuid.uuid4().hex[:8]}", **payload.model_dump())
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service


@router.delete("/{service_id}")
async def delete_service(service_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    await db.delete(service)
    await db.commit()
    return {"success": True, "message": f"Service {service_id} deleted"}
