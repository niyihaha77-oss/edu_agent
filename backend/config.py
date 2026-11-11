from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    配置类，用于加载环境变量
    """
    db_host: str = ""
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    # @property的特点是类似计算属性
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    # ── Milvus 向量库 ──
    milvus_host: str = "localhost"
    milvus_port: int = 19531  # 本机 19530 已占用，隔离到 19531

    # ── 大模型（DeepSeek）──
    deepseek_api_key: str  # 必填：DeepSeek 的 API Key
    deepseek_base_url: str = "https://api.deepseek.com/v1"  # DeepSeek 接口地址
    deepseek_model_chat: str = "deepseek-chat"  # 对话模型名
    deepseek_model_coder: str = "deepseek-coder"  # 代码模型名

    # ── 本地模型权重路径 ──
    reranker_model_path: str = "./models/reranker/bge-reranker-large"  # 精排模型
    classifier_model_path: str = "./models/classifier/all-MiniLM-L6-v2"  # 意图分类模型
    bge_m3_model_path: str = "./models/embedding/bge-m3"  # 嵌入模型

    # ── JWT 认证 ──
    jwt_secret_key: str  # 必填：签发登录令牌用的密钥
    jwt_algorithm: str = "HS256"  # 签名算法
    jwt_access_token_expire_minutes: int = 10080  # 令牌有效期（分钟）

    # ── MCP Server 地址（第五章用）──
    kb_mcp_server_url: str = "http://localhost:8000/mcp/kb"
    web_search_mcp_url: str = "http://localhost:8000/mcp/web-search"

    # ── Web 搜索（Tavily 可选；留空则自动用免费的 DuckDuckGo）──
    tavily_api_key: str = ""

    # ── 应用基础配置 ──
    app_env: str = "local"  # 运行环境标识
    app_debug: bool = False  # 是否调试模式
    app_host: str = "0.0.0.0"  # 监听地址
    app_port: int = 8000  # 监听端口
    log_level: str = "INFO"  # 日志级别
    default_tenant_id: str = "tenant_default"  # 多租户默认值

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding='utf-8',
        case_sensitive=False,# 大小写不敏感
        extra="ignore",
    )
@lru_cache()
def get_settings() -> Settings:
    return Settings()