import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from contextlib import contextmanager

# Load .env file
load_dotenv()

# Read DB URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in .env")

# Create engine
engine = create_engine(DATABASE_URL, future=True)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)

Base = declarative_base()

print("🔥 USING DATABASE:", DATABASE_URL)


# -----------------------------------------------------
# ⭐ FIX: Always force timezone UTC at session startup
# -----------------------------------------------------
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        # Force this session to use UTC timezone
        db.execute(text("SET TIMEZONE = 'UTC';"))
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
