from datetime import datetime, timedelta

from fastapi import APIRouter, Depends

from api.security import get_current_user
from api.tasks import perform_scrape

router = APIRouter()

@router.get("/trigger", summary="Trigger the Scraping to start updating the Database", status_code=200)
async def trigger_scraping(current_user: dict = Depends(get_current_user)):
    from api.main import scheduler
    scheduler.add_job(
        perform_scrape,
        trigger="date",
        run_date=datetime.now() + timedelta(seconds=2),  # This extra seconds was necessary in order to run it on docker
        id="initial_scrape",
        replace_existing=True
    )


