from http.client import HTTPException
from typing import Optional, List

from fastapi import APIRouter, Depends, Path, Query

from api.models.book import Book
from api.security import get_current_user
from api.services.book_service import BookService, get_book_service

router = APIRouter()

@router.get(
    "/",
    summary="List all books",
    status_code=200,
    response_model=List[Book]
)
async def list_books(current_user: dict = Depends(get_current_user),
                     book_service: BookService = Depends(get_book_service)):
    """
    Retorna todos os livros cadastrados no sistema.

    ### Requisitos de autenticação
    - Necessário autenticar via **JWT Bearer Token**.
    - Usuários não autenticados recebem **401 Unauthorized**.

    ### Response
    - **200 OK**: Lista de livros no formato:
      ```json
      [
        {
          "id": 1,
          "title": "Example Book",
          "category": "Travel",
          "price": "Â£45.17",
          "rating": "Two",
          "availability": "In stock (19 available)",
          "detail_page": "https://books.toscrape.com/catalogue/example/index.html",
          "image_url": "https://books.toscrape.com/catalogue/category/media/cache/6d/41/6d418a73cc7d4ecfd75ca11d854041db.jpg"
        },
        ...
      ]
      ```
    - **401 Unauthorized**: Token inválido ou ausente.
    """
    return book_service.list_books()

@router.get(
    "/",
    summary="List all books",
    status_code=200,
    response_model=List[Book]
)
async def search_books(title: Optional[str] = Query(None, description="Title to search"),
                       category: Optional[str] = Query(None, description="Category to search"),
                       page: int = Query(1, ge=1, description="Page number"),
                       size: int = Query(10, ge=1, le=100, description="Number of results per page"),
                       current_user: dict = Depends(get_current_user),
                       book_service: BookService = Depends(get_book_service)):
    """
       Busca livros por título e/ou categoria.

       ### Parâmetros de busca
       - **title** *(opcional)*: Texto a ser buscado no título dos livros.
       - **category** *(opcional)*: Nome exato da categoria.

       ### Requisitos de autenticação
       - Necessário autenticar via **JWT Bearer Token**.

       ### Response
       - **200 OK**: Lista de livros que correspondem aos filtros informados.
       - **401 Unauthorized**: Token inválido ou ausente.
       - **200 OK** com lista vazia: Nenhum livro encontrado.
       """
    return book_service.search_books(title=title, category=category)
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

@router.get(
    "/{book_id}",
    summary="Get book by ID",
    status_code=200,
    response_model=Book
)
async def get_book(book_id: int = Path(..., description="ID of the book to retrieve"),
                   current_user: dict = Depends(get_current_user),
                   book_service: BookService = Depends(get_book_service)):

    """
    Retorna os detalhes de um livro específico pelo seu ID.

    ### Requisitos de autenticação
    - Necessário autenticar via **JWT Bearer Token**.

    ### Parâmetros
    - **book_id** *(path)*: ID do livro.

    ### Response
    - **200 OK**: Objeto JSON com os dados do livro.
    - **404 Not Found**: Livro não encontrado.
    - **401 Unauthorized**: Token inválido ou ausente.
    """
    book = book_service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
