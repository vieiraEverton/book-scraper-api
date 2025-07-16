from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import settings
from api.db import init_db, engine
from api.routers import books, auth
from api.services.user_service import UserService
from api.tasks import scrape_and_store

app = FastAPI(
    title="Book Scraper API",
    version="0.1.0",
    description="API for querying books via scraping",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(books.router, prefix="/api/v1/books", tags=["Books"])
app.include_router(auth.router)

scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")

@app.on_event("startup")
def start_scheduler():
    scheduler.add_job(
        scrape_and_store,
        trigger="date",
        run_date=datetime.now(),
        id="initial_scrape",
        replace_existing=True
    )

    scheduler.add_job(
        scrape_and_store,
        trigger="interval",
        hours=1,
        id="scrape_job",
        replace_existing=True
    )
    scheduler.start()

@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()

@app.on_event("startup")
def on_startup():
    # 1) create tables
    init_db()

    # 2) seed admin user if missing
    from sqlmodel import Session

    with Session(engine) as session:
        user_service = UserService(session)
        admin = user_service.get_user_by_username("admin")
        if not admin:
            # choose a secure default or read from env
            default_password = settings.ADMIN_PASSWORD
            user_service.create_user(username="admin", password=default_password, is_admin=True)
            print("Admin user created with username='admin' and password=", default_password)


# --- Healthcheck ---
@app.get("/api/v1/health", tags=["Health"], status_code=200)
async def health():
    return {"status": "ok"}
