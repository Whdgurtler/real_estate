import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool


Base = declarative_base()


def create_database(database_url: str | None = None):
    url = database_url or os.getenv("DATABASE_URL", "sqlite:///./realestate.db")
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    options = {}
    if url.startswith("sqlite:"):
        options["connect_args"] = {"check_same_thread": False}
        if url in {"sqlite://", "sqlite:///:memory:"}:
            options["poolclass"] = StaticPool
    return create_engine(url, future=True, **options)


def create_session_factory(engine):
    return sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)


def ensure_postgis(engine):
    if engine.dialect.name != "postgresql":
        return
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        connection.execute(
            text("ALTER TABLE properties ADD COLUMN IF NOT EXISTS location geometry(Point, 4326)")
        )
        connection.execute(
            text(
                """
                UPDATE properties
                SET location = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
                WHERE longitude IS NOT NULL AND latitude IS NOT NULL AND location IS NULL
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE OR REPLACE FUNCTION sync_property_location() RETURNS trigger AS $$
                BEGIN
                    IF NEW.latitude IS NULL OR NEW.longitude IS NULL THEN
                        NEW.location = NULL;
                    ELSE
                        NEW.location = ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
                    END IF;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql
                """
            )
        )
        connection.execute(text("DROP TRIGGER IF EXISTS sync_property_location_trigger ON properties"))
        connection.execute(
            text(
                """
                CREATE TRIGGER sync_property_location_trigger
                BEFORE INSERT OR UPDATE OF latitude, longitude ON properties
                FOR EACH ROW EXECUTE FUNCTION sync_property_location()
                """
            )
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_properties_location "
                "ON properties USING GIST (location)"
            )
        )
