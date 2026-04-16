import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from modules.ai.service import ai_service

async def main():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    
    async with engine.begin() as conn:
        from core.database import Base
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        resp = await ai_service.get_chat_response(
            db=session,
            message="schedule science on 18th april 5pm topic physics and mentor gmail is test12@gmail.com",
            history=[]
        )
        print(f"Action: {resp.suggested_action}")

if __name__ == "__main__":
    asyncio.run(main())
