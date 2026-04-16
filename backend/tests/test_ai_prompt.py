import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from modules.ai.service import ai_service
from modules.ai.schemas import ChatMessage

async def main():
    # Use an in-memory db for testing
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    
    async with engine.begin() as conn:
        from core.database import Base
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        resp = await ai_service.get_chat_response(
            db=session,
            message="Schedule Math tomorrow at 10 AM, topic Algebra. Add mentor alok@example.com",
            history=[]
        )
        print(f"Response: {resp.response}")
        print(f"Action: {resp.suggested_action}")
        print(f"Force: {resp.force_execute}")

if __name__ == "__main__":
    asyncio.run(main())
