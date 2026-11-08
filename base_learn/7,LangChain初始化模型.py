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


class Offer(BaseModel):
    company_name:str = Field(description='公司名称')
    position:str = Field(description='职位')
    salary:int = Field(description='薪水')
    city:str = Field(description='城市')
    go_date:str = Field(description='入职日期')
    user_name:str = Field(description='姓名')
    ...
context = '''
    尊敬的tp同学,非常荣幸的通知你,你通过了面试,欢迎你入职陈泽传媒,
    我们的集团位于上海,你将担任AI算法工程师职位,薪水20000.23,城市上海,入职日期2026-12-16,姓名tp
    您需要在2026-12-16之前到上海报道,完成入职并办理手续
    
'''

text = f'''
你需要从给定的文本中提取出offer信息,{context}

'''
async def get_structed_data():
    struct_llm = llm.with_structured_output(Offer,method='function_calling') # 可产生结构化数据的发模型对象
    res:Offer = await struct_llm.ainvoke(text)
    print(res.model_dump())
    ...



asyncio.run(get_structed_data())








