from http.client import HTTPException
from typing import Optional

from fastapi import APIRouter, Depends, Path, Query

from api.security import get_current_user
from api.services.book_service import BookService, get_book_service

router = APIRouter()

@router.get("/", summary="List all books", status_code=200)
async def list_books(current_user: dict = Depends(get_current_user),
                     book_service: BookService = Depends(get_book_service)):
    return book_service.list_books()

@router.get("/search", summary="Search books", status_code=200)
async def search_books(title: Optional[str] = Query(None, description="Title to search"),
                       category: Optional[str] = Query(None, description="Category to search"),
                       page: int = Query(1, ge=1, description="Page number"),
                       size: int = Query(10, ge=1, le=100, description="Number of results per page"),
                       current_user: dict = Depends(get_current_user),
                       book_service: BookService = Depends(get_book_service)):
    offset = (page - 1) * size
    return book_service.search_books(title=title, category=category, limit=size, offset=offset)

@router.get("/top-rated", summary="Get the top-rated books", status_code=200)
async def top_rated(page: int = Query(1, ge=1, description="Page number"),
                    size: int = Query(10, ge=1, le=100, description="Number of results per page"),
                    current_user: dict = Depends(get_current_user),
                    book_service: BookService = Depends(get_book_service)):
    offset = (page - 1) * size
    return book_service.get_top_books(limit=size, offset=offset)

@router.get("/price-range", summary="Filter books by price range", status_code=200)
async def filter_books_by_price(min: Optional[float] = Query(None, description="Minimum price"),
                                max: Optional[float] = Query(None, description="Maximum price"),
                                page: int = Query(1, ge=1, description="Page number"),
                                size: int = Query(10, ge=1, le=100, description="Number of results per page"),
                                current_user: dict = Depends(get_current_user),
                                book_service: BookService = Depends(get_book_service)):
    offset = (page - 1) * size
    return book_service.filter_by_price_range(min_price=min, max_price=max, limit=size, offset=offset)

@router.get("/{book_id}", summary="Get book by ID", status_code=200)
async def get_book(book_id: int = Path(..., description="ID of the book to retrieve"),
                   current_user: dict = Depends(get_current_user),
                   book_service: BookService = Depends(get_book_service)):
    book = book_service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
