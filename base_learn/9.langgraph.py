import re
import uuid
from enum import auto,StrEnum
from typing import TypedDict,Annotated

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages



class ClassIfyEnum(StrEnum):
    CONCEPT = auto()
    CODE = auto()
    CHAT = auto()
class HelperState(TypedDict):
    question: str      # 用户的问题（输入）
    category: ClassIfyEnum      # 分类结果：concept / code / chat（中间结果）
    answer:   str      # 最终回应（输出）\
    code_loop:int # code 循环次数
    messages:Annotated[list,add_messages]# Annotated


def classify_node(state:HelperState):
    q = state['question']# 取到用户提的问题
    # 判断q里面是否包含某些数据
    res = re.search(r'(bug|代码|错误|报错|调试)',q)
    if res:
        state['category'] = ClassIfyEnum.CODE
    res = re.search(r'(概念|知识|解释)',q)
    if res:
        state['category'] = ClassIfyEnum.CONCEPT
    res = re.search(r'(聊天|说|告诉)',q)
    if res:
        state['category'] = ClassIfyEnum.CHAT

    return {'category':state['category']}
def code_node(state:HelperState):
    return {'answer':'I am a chatbot. I can help you with coding questions.','code_loop':state['code_loop']+1,"messages":f'code{state["code_loop"]}'}

def chat_node(state:HelperState):
    return {'answer':'I am a chatbot. I can help you with any questions.'}

def concept_node(state:HelperState):
    return {'answer':'I am a chatbot. I can help you with any questions.'}

def _router_map(state:HelperState) ->str:
    return state['category']

def _code_loop(state:HelperState) ->str:
    return "code" if state["code_loop"] < 3 else "end"
# 1.建图 建节点 连线  编译  运行
# 建图的时候 不传  状态 只是告诉你  这个图编排State是什么类型
builder = StateGraph(HelperState)
builder.add_node("classify",classify_node)
builder.add_node("code",code_node)
builder.add_node("chat",chat_node)
builder.add_node("concept",concept_node)
builder.add_edge(START,"classify")
# 添加条件边
builder.add_conditional_edges('classify',_router_map,
                              {"code":"code","chat":"chat","concept":"concept"})

builder.add_conditional_edges('code',_code_loop,
                              {"code":"code","end":END})


builder.add_edge('chat',END)
builder.add_edge('concept',END)
# builder.add_edge('classify','code')
# builder.add_edge('code',END)
config = {"configurable": {"thread_id": str(uuid.uuid4())}}
graph = builder.compile(checkpointer=MemorySaver()) # 编译的到可运行的图
res = graph.invoke({
    "question":"你帮我看一下这个代码",
    "category":"",
    "answer":"",
    "code_loop":0,
    "messages":''
},config=config)
print(res)