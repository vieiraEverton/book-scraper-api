from fastapi import APIRouter, Depends

from api.security import get_current_user
from api.services.category_service import CategoryService, get_category_service

router = APIRouter()

@router.get("/", summary="List all categories", status_code=200)
async def list_categories(current_user: dict = Depends(get_current_user),
                     category_servoce: CategoryService = Depends(get_category_service)):
    return category_servoce.list_categories()


