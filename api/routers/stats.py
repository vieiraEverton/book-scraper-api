from fastapi import APIRouter, Depends, Path, Query

from api.metrics_store import metrics_lock, metrics
from api.security import get_current_user
from api.services.book_service import BookService, get_book_service

router = APIRouter()

@router.get("/overview", summary="Get book statistics overview", status_code=200)
async def stats_overview(
    current_user: dict = Depends(get_current_user),
    book_service: BookService = Depends(get_book_service)
):
    return book_service.get_overview_stats()

@router.get("/categories", summary="Get statistics by category", status_code=200)
async def stats_by_category(
    current_user: dict = Depends(get_current_user),
    book_service: BookService = Depends(get_book_service)
):
    return book_service.get_category_stats()

@router.get("/performance", summary="Get performance metrics")
async def performance_stats():
    with metrics_lock:
        avg_time = metrics["total_time"] / metrics["total_requests"] if metrics["total_requests"] > 0 else 0.0
        per_path_stats = {
            path: {
                "count": data["count"],
                "average_time_ms": round((data["total_time"] / data["count"]) * 1000, 2)
            }
            for path, data in metrics["per_path"].items()
        }

    return {
        "total_requests": metrics["total_requests"],
        "average_response_time_ms": round(avg_time * 1000, 2),
        "per_path": per_path_stats
    }