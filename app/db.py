# app/db.py
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel

from app.settings import settings


# -----------------------
# DB URL helper (preserve your logic)
# -----------------------
def get_database_url() -> str:
    db_url = settings.database_url
    if not db_url:
        raise RuntimeError("DATABASE URL is not set in settings.database_url")

    # Convert sync psycopg2 URL to asyncpg if present
    if db_url.startswith("postgresql+psycopg2"):
        db_url = db_url.replace("psycopg2", "asyncpg")
    # Accept bare "postgresql://" -> convert to asyncpg
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Convert sqlite to aiosqlite driver if needed
    if db_url.startswith("sqlite://") and not db_url.startswith("sqlite+aiosqlite://"):
        db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://", 1)

    return db_url


# -----------------------
# Engine & session factory
# -----------------------
DATABASE_URL = get_database_url()

engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=bool(getattr(settings, "debug", False)),
    future=True,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# -----------------------
# FastAPI dependency
# -----------------------
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that yields an AsyncSession for FastAPI endpoints.
    Usage:
        async def endpoint(session: AsyncSession = Depends(get_async_session)):
            ...
    """
    async with AsyncSessionLocal() as session:
        yield session


# -----------------------
# DB initialization helper
# -----------------------
async def init_db() -> None:
    """
    Create database tables from SQLModel metadata.
    Call this on FastAPI startup (app.on_event('startup')).
    """
    # Ensure all model modules are imported before calling this so metadata is complete.
    # e.g. in app/main.py: `import app.models  # noqa: F401`
    async with engine.begin() as conn:
        # ensure pgvector extension exists in this database (PostgreSQL only)
        if DATABASE_URL.startswith("postgresql"):
            try:
                await conn.run_sync(lambda sync_conn: sync_conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;")))
            except Exception as e:
                print(f"Warning: Could not create pgvector extension: {e}")
        
        # then create tables
        await conn.run_sync(SQLModel.metadata.create_all)
        
        # run migrations (PostgreSQL only)
        if DATABASE_URL.startswith("postgresql"):
            await _run_schema_migrations(conn)


async def _run_schema_migrations(conn) -> None:
    """Apply schema migrations for constraints and indexes."""
    migrations = [
        # Create unique constraint on (checksum, status)
        """
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE table_name='pdffile' AND constraint_name='uq_pdffile_checksum_status'
            ) THEN
                ALTER TABLE pdffile 
                ADD CONSTRAINT uq_pdffile_checksum_status UNIQUE (checksum, status);
            END IF;
        END $$;
        """
    ]

    for sql in migrations:
        try:
            await conn.execute(text(sql))
        except Exception:
            pass

