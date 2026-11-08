import asyncio
import os

from langchain.chat_models import init_chat_model

from langchain.messages import SystemMessage,AIMessage,HumanMessage
from pydantic import BaseModel, Field
llm = init_chat_model(
    model="deepseek-chat",                       # 模型名称
    model_provider="openai",                     # 走 OpenAI 兼容协议（关键）
    api_key=os.getenv("DEEPSEEK_API_KEY"),                # DeepSeek 的 API Key
    base_url="https://api.deepseek.com/v1",      # DeepSeek 接口地址（关键）
    temperature=0,                               # 输出的随机性，0 = 最稳定
)

# 给我写一个赞美我的文章


async def get_article():
    async for chunk in llm.astream("我是你的爸爸,写一个一万字的长文赞美一下我,我每天不仅要照顾你,还要忙着减肥,我4个月瘦了50斤,总算有了结果."):
        print(chunk.text,end='',flush=True)
    ...
asyncio.run(get_article())