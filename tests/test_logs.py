from backend.core.logger import configure_logging,get_logger

configure_logging()

logger = get_logger(__name__)

logger.info("qa的向量检索",a=1,b=2)