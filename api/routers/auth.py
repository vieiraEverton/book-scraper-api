from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlmodel import Session

from api.db import get_session
from api.security import (
    create_access_token, create_refresh_token, decode_token, )
from api.services.user_service import UserService

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

class TokenRefreshRequest(BaseModel):
    refresh_token: str

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user_service = UserService(session)
    user = user_service.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token  = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", summary="Refresh access token")
def refresh(request: TokenRefreshRequest):
    payload = decode_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    new_access_token = create_access_token(data={"sub": username})
    return {"access_token": new_access_token, "token_type": "bearer"}
