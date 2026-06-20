import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 👈 Changed driver to standard sqlite (no aiosqlite or greenlet needed)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./national_hockey_league.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Factory function helper to get a database thread context
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
