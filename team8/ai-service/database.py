import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base

DATABASE_URL = os.getenv("AI_DATABASE_URL", "postgresql://ai_user:ai_pass@localhost:5434/ai_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Dependency for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Note: Database schema is managed by Alembic migrations
# To create/update tables, use:
#   alembic revision --autogenerate -m "description"
#   alembic upgrade head
