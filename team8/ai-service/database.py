"""
Database connection and session management for AI Service
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base

# Get database URL from environment variable
DATABASE_URL = os.getenv(
    "AI_DATABASE_URL",
    "postgresql://ai_user:ai_pass@ai-postgres:5432/ai_db"
)

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Dependency for getting database session
    Usage in FastAPI:
        @app.post("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables (only if they don't exist)
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
