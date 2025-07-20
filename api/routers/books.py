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
                       current_user: dict = Depends(get_current_user),
                       book_service: BookService = Depends(get_book_service)):
    return book_service.search_books(title=title, category=category)

@router.get("/{book_id}", summary="Get book by ID", status_code=200)
async def get_book(book_id: int = Path(..., description="ID of the book to retrieve"),
                   current_user: dict = Depends(get_current_user),
                   book_service: BookService = Depends(get_book_service)):
    book = book_service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
