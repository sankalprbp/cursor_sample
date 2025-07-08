"""
Logging Configuration
Sets up application-wide logging
"""

import logging
import sys
from typing import Any
from loguru import logger

from app.core.config import settings


class InterceptHandler(logging.Handler):
    """
    Intercept standard logging messages and redirect them to loguru
    """
    def emit(self, record: logging.LogRecord) -> Any:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    """
    Configure logging for the application
    """
    # Remove default logger
    logger.remove()
    
    # Add console handler with custom format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.LOG_LEVEL,
        colorize=True,
    )
    
    # Add file handler if in production
    if settings.ENVIRONMENT == "production":
        logger.add(
            "logs/app_{time}.log",
            rotation="500 MB",
            retention="10 days",
            format=log_format,
            level=settings.LOG_LEVEL,
            compression="zip",
        )
    
    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Set logging level for specific libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    logger.info(f"Logging configured with level: {settings.LOG_LEVEL}")


# Initialize logging when module is imported
setup_logging()

# Export logger for use in other modules
__all__ = ["logger"]