import asyncio
import json

from fastapi import FastAPI
from sse_starlette import EventSourceResponse

app = FastAPI()
# 异步生成器
async def event_generator():
    content = "我是你爸爸,快叫爸爸,乖儿子"
    for i in content:
        await asyncio.sleep(0.3)
        yield {"data":json.dumps({"type":'token',"content":i},ensure_ascii=False)}
    yield {"data":json.dumps({"type":'done'})}# 结束标记

@app.get("/chat/stream")
async def get_chat_stream():
    return EventSourceResponse(event_generator())# 需要一个异步生成器

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app,host='0.0.0.0', port=8020)
    pass
