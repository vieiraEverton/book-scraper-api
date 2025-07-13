from sqlmodel import SQLModel, create_engine, Session
import os

os.makedirs("data", exist_ok=True)

DATABASE_URL = "sqlite:///./data/bookapi.db"
engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False}
)

def init_db():
    """
    Create all tables.
    Call this at app startup.
    """
    SQLModel.metadata.create_all(engine)

def get_session():
    """
    FastAPI dependency to get a DB session.
    """
    with Session(engine) as session:
        yield session
