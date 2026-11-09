import asyncio
from contextlib import asynccontextmanager


@asynccontextmanager
async def test():
    print("准备前工作")
    yield '异步'
    print('结束')

async def main():
    async with test() as f:
        print(f)


asyncio.run(main())