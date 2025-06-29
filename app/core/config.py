from sqlalchemy.ext.asyncio import create_async_engine
from databases import Database

DATABASE_URL = "sqlite+aiosqlite:///./pkb.db"

# async SQLAlchemy engine
engine = create_async_engine(DATABASE_URL, echo=True)

# async connection (used with Databases)
database = Database(DATABASE_URL)
