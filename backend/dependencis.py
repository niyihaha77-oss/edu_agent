from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession

engine = create_async_engine(
    url="来自config",
    pool_size=10,# 连接池大小
    max_overflow=20,# 连接池最大溢出数
)
AsyncSessionLocal = async_sessionmaker(engine,expire_on_commit=False)

# Depends给 fastapi 提供使用
# Depends可以依赖 普通函数   异步函数  异步生成器
async def get_db() -> AsyncGenerator[AsyncSession,None]:  # 第一个参数表示yield后边返回什么东西
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise
    pass