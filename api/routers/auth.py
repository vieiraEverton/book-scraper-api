from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlmodel import Session

from api.db import get_session
from api.security import (
    create_access_token, create_refresh_token, decode_token, )
from api.services.user_service import UserService

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

class TokenPair(BaseModel):
    access_token: str = Field(..., description="JWT de acesso (curta duração)")
    refresh_token: str = Field(..., description="JWT de refresh (longa duração)")
    token_type: str = Field("bearer", description="Tipo do token")

class AccessTokenResponse(BaseModel):
    access_token: str = Field(..., description="Novo JWT de acesso")
    token_type: str = Field("bearer", description="Tipo do token")

class TokenRefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="JWT de refresh obtido no /login")

@router.post(
    "/login",
    summary="Login (Password Grant)",
    response_model=TokenPair,
    responses={
        401: {"description": "Invalid credentials"},
    },
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """
    Autentica o usuário e retorna **access_token** e **refresh_token**.

    ### Como chamar
    - **Content-Type**: `application/x-www-form-urlencoded`
    - **Campos**: `username`, `password` (e opcionalmente `scope`)

    ### Exemplo (curl)
    ```bash
    curl -X POST "http://localhost:8000/api/v1/auth/login" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "username=john&password=secret"
    ```

    ### Response 200 (exemplo)
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI...",
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI...",
      "token_type": "bearer"
    }
    ```
    """
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

@router.post(
    "/refresh",
    summary="Refresh access token",
    response_model=AccessTokenResponse,
    responses={
        401: {"description": "Invalid refresh token"},
    },
)
def refresh(request: TokenRefreshRequest):
    """
    Gera um **novo access_token** a partir de um **refresh_token** válido.

    - Não altera/renova o refresh token.
    - Útil para manter a sessão ativa sem pedir usuário/senha novamente.

    ### Exemplo (curl)
    ```bash
    curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
      -H "Content-Type: application/json" \
      -d '{"refresh_token":"<seu-refresh-token>"}'
    ```

    ### Response 200 (exemplo)
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI...",
      "token_type": "bearer"
    }
    ```
    """
    payload = decode_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    new_access_token = create_access_token(data={"sub": username})
    return {"access_token": new_access_token, "token_type": "bearer"}
