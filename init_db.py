from app.core.models import Base
from app.core.config import engine
import asyncio

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init_models())
