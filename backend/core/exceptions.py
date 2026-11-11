from http.client import HTTPException


class EduAgentBaseError(Exception):
    def __init__(self,message:str,agent_type:str = '',detail:dict = None):
        super().__init__(message)
        self.agent_type = agent_type
        self.details = detail or {}
        pass

class LLMAPIError(EduAgentBaseError):
    """大模型 API 调用失败（超时 / 限流 / 网络错误）。属于【可重试】异常。"""
    pass                                   # 无需额外逻辑，直接继承基类的能力即可


class AgentExecutionError(EduAgentBaseError):
    """Agent 业务逻辑执行失败。"""
    pass


class PipelineError(EduAgentBaseError):
    """多 Agent Pipeline（流水线编排）失败。"""
    pass


class IntentRouteError(EduAgentBaseError):
    """意图识别路由失败（没判断出该交给哪个 Agent）。"""
    pass


class MilvusConnectionError(EduAgentBaseError):
    """Milvus 向量库连接失败。属于【可重试】异常。"""
    pass


class FileParseError(EduAgentBaseError):
    """文件解析失败（Word / PDF）。"""
    pass


class InvalidInputError(EduAgentBaseError):
    """用户输入不合法。属于【不可重试】异常（重试也不会变合法）。"""
    pass


class AuthenticationError(EduAgentBaseError):
    """认证失败。属于【不可重试】异常。"""
    pass