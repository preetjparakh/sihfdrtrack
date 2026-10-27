import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

MOCK_BANK_DB_URL = os.getenv("MOCK_BANK_DB_URL", "sqlite:///./mock_bank.db")

engine_args = {}
if MOCK_BANK_DB_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(MOCK_BANK_DB_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_bank_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
