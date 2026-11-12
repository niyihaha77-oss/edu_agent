# 提供自由文本输出的模型
from dataclasses import dataclass
from typing import Type

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable

from enum import StrEnum, auto, unique

from pydantic import BaseModel, Field

from backend.config import get_settings


class ModelType(StrEnum):
    DEEPSEEK_CHAT=get_settings().deepseek_model_chat
    DEEPSEEK_MODEL_CODER=get_settings().deepseek_model_coder
@unique # 表示不同的枚举名称 得到的值不能一样
class AgentType(StrEnum):
    QA=auto()
    EXAM=auto()
    INTERVIEW=auto()
    RESUME=auto()
    GENERAL = auto()
    UNKNOWN = auto()
# langchain所需要的大模型配置信息

class LLMConfig(BaseModel):
    """LLM 配置"""
    provider: str
    model: str
    max_tokens: int = 2048
    temperature: float = 0.0
    streaming: bool = False
    thinking: bool = False
# 4个智能体的大模型对应不同的配置
LLM_ROUTING = {
    AgentType.QA: LLMConfig(
        provider='openai',
        model=ModelType.DEEPSEEK_CHAT,
        max_tokens=2048,
        temperature=0.2,
        streaming=True,
    ),
    AgentType.RESUME: LLMConfig(
        provider='openai',
        model=ModelType.DEEPSEEK_CHAT,
        max_tokens=8192,
        temperature=0,
        streaming=False,
    ),
    AgentType.GENERAL: LLMConfig(
        provider='openai',
        model=ModelType.DEEPSEEK_CHAT,
        max_tokens=1024,
        temperature=0.3,
        streaming=True,
    ),
    AgentType.EXAM: LLMConfig(
        provider='openai',
        model=ModelType.DEEPSEEK_CHAT,
        max_tokens=4096,
        temperature=0,
        streaming=False,
    ),
    AgentType.INTERVIEW: LLMConfig(
        provider='openai',
        model=ModelType.DEEPSEEK_MODEL_CODER,
        max_tokens=2048,
        temperature=0.3,
        streaming=True,
    )
}
class LLMFactory:
    @classmethod
    def get_llm(cls, agent_type: AgentType|str) -> BaseChatModel:
        config = LLM_ROUTING[agent_type].model_dump()
        # config["api_key"] = get_settings().deepseek_api_key
        # config["base_url"] = get_settings().deepseek_base_url
        config = {
            "api_key": get_settings().deepseek_api_key,
            "base_url": get_settings().deepseek_base_url,
            "model_provider": "openai",
            "temperature": config["temperature"],
            "model": config["model"]
        }
        return init_chat_model(**config)
    pass


# 字典{key(agentType): value(LLMConfig)}，表示不同智能体对应不同的大模型配置
def get_llm(agent_type:AgentType | str) ->BaseChatModel:
    return LLMFactory.get_llm(agent_type)


    pass

def get_structured_llm(agent_type:AgentType| str,schema:Type[BaseModel])->Runnable:
    llm = get_llm(agent_type)
    return llm.with_structured_output(method="function_calling", schema=schema)

    pass

if __name__ == '__main__':
    llm = get_llm(AgentType.QA)


    res = llm.invoke("我测")
    print(res.content)
    class Person(BaseModel):
        name: str = Field(description='姓名')
        age: int = Field(description='年龄')
    llm = get_structured_llm(AgentType.QA, Person)
    res  = llm.invoke("杨幂的个人信息")
    print(res.model_dump())
