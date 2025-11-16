import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from app.config import settings

logger = logging.getLogger(__name__)

# Convert DATABASE_URL for asyncpg
DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def init_db():
    from app.models import User
    from app.api.auth import get_password_hash

    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Seed initial data if needed
    async with AsyncSession(engine) as session:
        # Check if a default user exists
        result = await session.execute(select(User).where(User.email == settings.SUPERUSER_EMAIL))
        if not result.scalar_one_or_none():
            logger.info("Creating superuser")
            user = User(
                email=settings.SUPERUSER_EMAIL,
                hashed_password=get_password_hash(settings.SUPERUSER_PASSWORD),
                is_superuser=True,
                telegram_id=settings.SUPERUSER_TELEGRAM_ID
            )
            session.add(user)
            await session.commit()
            logger.info("Superuser created")

async def get_db():
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        yield session