'''
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
'''
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Dynamically configure connection URL depending on active system run flags
IS_TESTING = (
    os.getenv("TESTING") == "true" or 
    "pytest" in sys.modules or 
    "pytest" in os.environ.get("PYTEST_CURRENT_TEST", "")
)

if IS_TESTING:
    # 👈 Combined parameters into the connection string cleanly without the invalid 'uri=True' argument
    DATABASE_URL = "sqlite:///file:test_mem_db?mode=memory&cache=shared"
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./national_hockey_league.db")
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
