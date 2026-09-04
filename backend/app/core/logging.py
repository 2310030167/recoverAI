import sys
import logging
from app.core.config import settings


class StructuredFormatter(logging.Formatter):
    """
    Structured application log formatter outputting clean, standard key-value
    or JSON-like formatted logs containing timestamp, level, logger, and message.
    """
    def format(self, record: logging.LogRecord) -> str:
        timestamp = self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z")
        log_entry = (
            f"timestamp={timestamp} "
            f"level={record.levelname} "
            f"logger={record.name} "
            f'message="{record.getMessage()}"'
        )
        if record.exc_info:
            log_entry += f" exc_info={self.formatException(record.exc_info)}"
        return log_entry


def setup_logging() -> logging.Logger:
    """
    Configure application-wide structured logger.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger = logging.getLogger("recoverai")
    logger.setLevel(log_level)

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(StructuredFormatter())
        logger.addHandler(console_handler)

    logger.propagate = False
    return logger


logger = setup_logging()
