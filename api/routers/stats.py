from fastapi import APIRouter, Depends, Path, Query

from api.security import get_current_user
from api.services.book_service import BookService, get_book_service

router = APIRouter()

@router.get("/stats/overview", summary="Get book statistics overview", status_code=200)
async def stats_overview(
    current_user: dict = Depends(get_current_user),
    book_service: BookService = Depends(get_book_service)
):
    return book_service.get_overview_stats()

@router.get("/stats/categories", summary="Get statistics by category", status_code=200)
async def stats_by_category(
    current_user: dict = Depends(get_current_user),
    book_service: BookService = Depends(get_book_service)
):
    return book_service.get_category_stats()