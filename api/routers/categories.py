from typing import List

from fastapi import APIRouter, Depends

from api.models.category import Category
from api.security import get_current_user
from api.services.category_service import CategoryService, get_category_service

router = APIRouter()

@router.get(
    "/",
    summary="List all categories",
    status_code=200,
    response_model=List[Category]
)
async def list_categories(
    current_user: dict = Depends(get_current_user),
    category_service: CategoryService = Depends(get_category_service)
):
    """
    Retorna a lista de todas as categorias cadastradas no sistema.

    ### Requisitos de autenticação
    - É necessário estar autenticado via JWT Bearer Token.
    - Usuários não autenticados receberão `401 Unauthorized`.

    ### Response
    - **200 OK**: Lista de categorias no formato:
      ```json
      [
        "Travel",
        "Science Fiction",
        "Mystery"
      ]
      ```
    - **401 Unauthorized**: Caso o token seja inválido ou ausente.

    ### Observações
    - Os nomes de categoria são retornados exatamente como armazenados no banco.
    - Não há paginação, todas as categorias são retornadas de uma vez.
    """
    return category_service.list_categories()
