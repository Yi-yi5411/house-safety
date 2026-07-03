import asyncio
from app.db.database import async_session_factory
from sqlalchemy import text
async def check():
    async with async_session_factory() as session:
        for ct in ['地基','基础','混凝土柱','砖柱']:
            result = await session.execute(text(f"SELECT COUNT(*) as cnt FROM evaluation_standards WHERE component_type='{ct}'"))
            print(f"{ct}: {result.scalar()}")
        result = await session.execute(text("SELECT COUNT(*) as cnt FROM evaluation_standards"))
        print(f"Total: {result.scalar()}")
asyncio.run(check())
