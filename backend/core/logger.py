import logging
import sys

from backend.config import get_settings


class Logger:

    def __init__(self,name:str):
        self.name = name

        self._log = logging.getLogger(name)
    # 将用户传递过来的参数组装成一个标准格式
    def _fmt(self,event:str,**kw)->str:
        if kw:
            return event + "|" + ",".join([f"{k}={v}" for k,v in kw.items()])
        return event

    def info(self,event:str,**kw):
        self._log.info(self._fmt(event,**kw))
        pass
    def debug(self,event:str,**kw):
        self._log.debug(self._fmt(event,**kw))
        pass
    def error(self,event:str,**kw):
        self._log.error(self._fmt(event,**kw))
        pass
    def warning(self,event:str,**kw):
        self._log.warning(self._fmt(event,**kw))
        pass
    def critical(self,event:str,**kw):
        self._log.critical(self._fmt(event,**kw))
        pass
# 对日志进行初始日志化
def configure_logging() -> None:
    """全局日志配置函数：整个应用只在启动时（main.py）调用一次。
    负责设定日志格式、级别，并压低第三方库的噪音日志。"""
    settings = get_settings()                  # 读配置，拿到 log_level（如 "INFO"）
    # getattr(logging, "INFO", 兜底) 把字符串级别转成 logging 模块里的常量 logging.INFO；
    # .upper() 先转大写；万一配置写错找不到该常量，就用 logging.INFO 兜底
    level = getattr(logging, settings.log_level.upper(), logging.INFO) # 从当前的配置文件中读取日志级别
    logging.basicConfig(                       # 标准库的「一键全局配置」
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",  # 格式：时间 [级别] 模块名: 内容
        stream=sys.stdout,                     # 把日志打到标准输出（控制台）
        level=level,                           # 全局生效的日志级别
        force=True,                            # 强制覆盖已有的日志配置（否则重复调用 basicConfig 会失效）
    )
    # 下面把几个第三方库的日志级别单独调到 WARNING，屏蔽它们大量的 INFO 噪音，避免刷屏
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)  # SQLAlchemy 的 SQL 执行日志
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)    # SQLAlchemy 连接池日志
    logging.getLogger("httpx").setLevel(logging.WARNING)              # httpx HTTP 客户端日志
    logging.getLogger("httpcore").setLevel(logging.WARNING)           # httpcore 底层日志

def get_logger(name:str)-> Logger:
    return Logger(name)