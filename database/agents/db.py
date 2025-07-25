from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

class DatabaseHandler:
    def __init__(self, database_url: str):
        self.engine: AsyncEngine = create_async_engine(
            database_url, pool_size=5, max_overflow=10, echo=True
        )
        self.session_factory = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    async def get_session(self):
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
