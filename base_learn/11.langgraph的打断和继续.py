import uuid
from typing import TypedDict,Annotated

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langgraph.types import interrupt, Command


class InterviewState(TypedDict):
    content:str # 学生面试表达
    comment:str # 老师的评价
    messages:Annotated[list,add_messages]




def interview_node(state:InterviewState):
    print(f"面试者:{state['content']}")
    return {}

def teach_node(state:InterviewState):
    comment = interrupt("请面试官作出对这个学生的评价")
    return {"comment":comment}
    ...
builder = StateGraph(InterviewState)

builder.add_node('stu_interview',interview_node)
builder.add_node('teacher',teach_node)
builder.add_edge(START, "stu_interview")
builder.add_edge("stu_interview", "teacher")
builder.add_edge("teacher", END)

config = {"configurable": {"thread_id": str(uuid.uuid4())}}
graph = builder.compile(checkpointer=MemorySaver())  # 编译   checkpointer保存状态


if __name__ == '__main__':
    res = graph.invoke(
        {
            "content":"我是一个学生",
            "comment":"",
            "messages":[]
        },config=config
    )
    comment = input('请面试官作出评价:')
    res1 = graph.invoke(Command(resume=comment),config=config)
    print(res1)
    # 走到这里,说明图停止了

    ...