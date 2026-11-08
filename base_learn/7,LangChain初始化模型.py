import asyncio
import os

from langchain.chat_models import init_chat_model

from langchain.messages import SystemMessage,AIMessage,HumanMessage

llm = init_chat_model(
    model="deepseek-chat",                       # 模型名称
    model_provider="openai",                     # 走 OpenAI 兼容协议（关键）
    api_key=os.getenv("DEEPSEEK_API_KEY"),                # DeepSeek 的 API Key
    base_url="https://api.deepseek.com/v1",      # DeepSeek 接口地址（关键）
    temperature=0,                               # 输出的随机性，0 = 最稳定
)
# res = llm.invoke('你好,现在程序员是不是完蛋了?100字以内')
#
# print(res.text)
# print('='*50)
# print(res.content)

async def get_message():
    res = await llm.ainvoke('我是你爸爸')
    print(res.text)

# asyncio.run(get_message())
async def teach_son():
    res = await llm.ainvoke(
        [SystemMessage(content="你是我儿子,你现在10个月,你爱拉屎,不喜欢吃奶,喜欢吃奶粉"),
         HumanMessage(content="叫爸爸")]
    )
    print(res.text)

asyncio.run(teach_son())
