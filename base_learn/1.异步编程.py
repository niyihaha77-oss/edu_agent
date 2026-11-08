import asyncio
import time


async def get_name(name:str):
    print(f"{name}开始执行")
    await asyncio.sleep(1)
    print(f"{name}执行结束")

async def main():
    start_time = time.time()
    await get_name('任务一')
    await get_name('任务二')
    await get_name('任务三')
    print(f"耗时:{time.time() - start_time}")


async def main2():
    start_time = time.time()
    # 使用gather实现并发
    await asyncio.gather(get_name('任务一'), get_name('任务二'), get_name('任务三'))
    print(f"耗时:{time.time() - start_time}")
asyncio.run(main2())
asyncio.run(main())