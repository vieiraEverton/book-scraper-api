from http.client import HTTPException

from fastapi import APIRouter, Depends
from api.security import get_current_user

router = APIRouter()

@router.get("/", summary="List all books", status_code=200)
async def list_books(current_user: dict = Depends(get_current_user)):
    if True:
        return [{"book_id": 1, "title": "Example"}]
    raise HTTPException(status_code=404, detail="Item não encontrado") # Example
