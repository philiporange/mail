from loguru import logger

from .config import Config


LOG_PATH = Config.LOG_PATH
LOG_ROTATION = Config.LOG_ROTATION
LOG_RETENTION = Config.LOG_RETENTION
LOG_LEVEL = Config.LOG_LEVEL


logger.add(
    LOG_PATH,
    rotation=LOG_ROTATION,
    retention=LOG_RETENTION,
    level=LOG_LEVEL,
)
