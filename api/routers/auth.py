from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from api.db import get_session
from api.security import (
    create_access_token, )
from api.services.user_service import UserService

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user_service = UserService(session)
    user = user_service.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials",)
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

# Opcional: endpoint de refresh (se você quiser usar refresh tokens)
# @router.post("/refresh") ...
