import json
import operator
import os

from fastapi import FastAPI,Request
import uvicorn
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated
import uuid
from langchain.chat_models import init_chat_model
from sse_starlette import EventSourceResponse
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from sqlalchemy import text
llm = init_chat_model(
    model='deepseek-chat',
    model_provider='openai',
    api_key = os.getenv("DEEPSEEK_API_KEY"),
    base_url = "https://api.deepseek.com/v1",
    temperature=0.1,
)

# 定义langgraph的节点状态
class ChatState(TypedDict):
    user_question:str
    messages:Annotated[list,operator.add]
# 第一个节点
async def chat_node(state:ChatState):
    question = state['user_question']
    response = await llm.ainvoke(question)
    return {"messages":[question]} # 会进行消息的合并

# 第二个节点
engine = create_async_engine(
    url='postgresql+asyncpg://eduagent_user:123456@localhost:15433/test',
    pool_size=10,# 连接池基础大小
    max_overflow=10,# 连接池最大溢出数
    echo=False,# 是否输出sql 改True 会打印出所有SQL,调试时可以临时打开
)
# expire_on_commit=False 指在连接过程中,不去更新内存数据
AsyncSessionLocal = async_sessionmaker(engine,expire_on_commit=False)
create_sql = """
create table if not exists chat_list_table(
    id uuid primary key default uuid_generate_v4(),
    content text,
    created timestamp default now()
    
)

"""
insert_sql = """
    insert into chat_list_table (content) values (:content)
"""
async def save_node(state:ChatState):
    question = state['user_question']# 用户提问的消息
    async with AsyncSessionLocal() as session:
        await session.execute(text(create_sql))
        await session.execute(text(insert_sql),{"content":question})
        await session.commit()
    return {}
# 获取唯一id
def _get_unique_id() -> str:
    return str(uuid.uuid4())

# 获取图配置
def _get_graph_config() ->dict:
    return {
        "configurable":{"thread_id":_get_unique_id()} # 获取唯一id
    }
# 搭图
builder = StateGraph(ChatState)
# 添加节点
builder.add_node("chat",chat_node)
builder.add_node("save",save_node)


# 添加边进行连线

builder.add_edge(START,"chat")
builder.add_edge("chat","save")
builder.add_edge("save",END)
# 构建图

graph = builder.compile(checkpointer=MemorySaver())

app = FastAPI(title='智能体综合小案例')


async def event_generator(prompt:str):
    # 监听graph中图节点的流式输出,给sse
    config = _get_graph_config() # 拿到启动graph的config
    # 该方法可以穿透node节点 拿到大模型的流式输出
    async for event in graph.astream_events({"user_question":prompt},config=config):  # graph.ainvoke(state,config)
        kind = event["event"]# 拿到流式输出事件名称
        if kind == "on_chat_model_stream":
            text = event["data"]["chunk"].content
            yield {"data":json.dumps({"type":'token',"content":text},ensure_ascii=False)}

    yield {"data":{"type":"done"}}
    pass
@app.get("/chat/stream")
async def get_chat_stream(request:Request,prompt:str):
    # request 可以拿到请求的参数也可以判断当前是否还和前端连着线
    connect = await request.is_disconnected() # 可以判断当前是否还和前端连着线
    if connect:
        return {"message":"客户端已断开连接"}
    if not prompt.strip():
        return {"message":"问题不能为空"}
    return EventSourceResponse(event_generator(prompt))

@app.get("/chat/list")
async def get_chat_list():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("select * from chat_list_table"))
        return {"data":result.mappings().all()}

# langgraph有时间监听机制 可以监听到节点中流的输出
if __name__ == '__main__':

    uvicorn.run(app, host='0.0.0.0', port=8888)

