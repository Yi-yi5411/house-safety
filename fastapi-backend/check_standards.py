import asyncio
from app.db.database import async_session_factory
from sqlalchemy import text

async def check():
    async with async_session_factory() as session:
        result = await session.execute(text("SELECT component_type, evaluation_result, evaluation_clause, sort_order FROM evaluation_standards WHERE component_type='地基' ORDER BY sort_order"))
        rows = result.fetchall()
        print("地基 standards:")
        for r in rows:
            print(f"  {r[3]}. {r[0]} | {r[1]} | {str(r[2])[:60]}")
        print(f"  Total: {len(rows)}")
        
        result = await session.execute(text("SELECT component_type, evaluation_result, evaluation_clause, sort_order FROM evaluation_standards WHERE component_type='基础' ORDER BY sort_order"))
        rows = result.fetchall()
        print("基础 standards:")
        for r in rows:
            print(f"  {r[3]}. {r[0]} | {r[1]} | {str(r[2])[:60]}")
        print(f"  Total: {len(rows)}")
        
        result = await session.execute(text("SELECT COUNT(*) FROM evaluation_standards"))
        print(f"Total standards: {result.scalar()}")

asyncio.run(check())
