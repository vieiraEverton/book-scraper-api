from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import time

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import structlog

from api.config import settings
from api.db import init_db, engine
from api.metrics_store import metrics_lock, metrics
from api.routers import books, auth, categories, scraping, stats, ml
from api.services.user_service import UserService
from api.tasks import perform_scrape, perform_initial_scrape

scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")
logger = structlog.get_logger()

def setup_database():
    print("Setting Up Database...")

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

def setup_scheduler():
    print("Setting Up Scheduler...")
    scheduler.add_job(
        perform_initial_scrape,
        trigger="date",
        run_date=datetime.now() + timedelta(seconds=5),  # This extra seconds was necessary in order to run it on docker
        id="initial_scrape",
        replace_existing=True
    )

    scheduler.add_job(
        perform_scrape,
        trigger="interval",
        hours=1,
        id="scrape_job",
        replace_existing=True
    )
    scheduler.start()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("Starting up...")
    setup_database()
    setup_scheduler()
    print("Setup Completed!")

    try:
        yield
    finally:
        print("Shutting down...")
        scheduler.shutdown(wait=False)
        print("Scheduler stopped.")

app = FastAPI(
    title="Book Scraper API",
    version="0.1.0",
    description="API for querying books via scraping",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(books.router, prefix="/api/v1/books", tags=["Books"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["Categories"])
app.include_router(scraping.router, prefix="/api/v1/scraping", tags=["Scraping"])
app.include_router(stats.router, prefix="/api/v1/stats", tags=["Stats"])
app.include_router(auth.router)
app.include_router(ml.router, prefix="/api/v1/ml", tags=["ML"])

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    logger.info(
        "api_call",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration * 1000, 2)
    )

    return response

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    with metrics_lock:
        metrics["total_requests"] += 1
        metrics["total_time"] += duration
        path = request.url.path
        metrics["per_path"][path]["count"] += 1
        metrics["per_path"][path]["total_time"] += duration

    return response

# --- Healthcheck ---
@app.get("/api/v1/health", tags=["Health"], status_code=200)
async def health():
    return {"status": "ok"}
