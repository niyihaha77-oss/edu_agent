import asyncio

from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from sqlalchemy import text
engine = create_async_engine(
    url='postgresql+asyncpg://eduagent_user:123456@localhost:15433/test',
    pool_size=10,# 连接池基础大小
    max_overflow=10,# 连接池最大溢出数
    echo=False,# 是否输出sql 改True 会打印出所有SQL,调试时可以临时打开
)
# expire_on_commit=False 指在连接过程中,不去更新内存数据
AsyncSessionLocal = async_sessionmaker(engine,expire_on_commit=False)


# with上下文管理器 AsyncSessionLocal支持with 调用 是一个 异步生成器
async def get_student_list():
    async with AsyncSessionLocal() as session:
        res = await session.execute(text("select * from teacher "))
        print(res.mappings().all()) # 更方便直接进行数据个类型的转化 直接转化Pydantic更简单,直接解包就行


if __name__ == '__main__':
    asyncio.run(get_student_list())