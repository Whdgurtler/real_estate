import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool


Base = declarative_base()


def create_database(database_url: str | None = None):
    url = database_url or os.getenv("DATABASE_URL", "sqlite:///./realestate.db")
    options = {}
    if url.startswith("sqlite:"):
        options["connect_args"] = {"check_same_thread": False}
        if url in {"sqlite://", "sqlite:///:memory:"}:
            options["poolclass"] = StaticPool
    return create_engine(url, future=True, **options)


def create_session_factory(engine):
    return sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
