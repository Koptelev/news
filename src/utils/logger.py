"""Logging configuration."""

import logging
import sys
from typing import Optional

from pydantic_settings import BaseSettings


class LoggingSettings(BaseSettings):
    """Settings for logging configuration."""

    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_prefix = ""
        extra = "ignore"  # Игнорировать дополнительные поля


def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Настройка логгера с форматированием.

    Args:
        name: Имя логгера
        level: Уровень логирования (если не указан, берется из env)

    Returns:
        Настроенный логгер
    """
    settings = LoggingSettings()
    log_level = level or settings.log_level

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

