from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from jose import jwt
from database import settings
from schemas import AdminLogin, TokenOut

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=TokenOut)
async def admin_login(payload: AdminLogin):
    if payload.username != settings.admin_username or payload.password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    token = jwt.encode(
        {"sub": payload.username, "role": "admin", "exp": expire},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    return {"access_token": token, "token_type": "bearer"}
