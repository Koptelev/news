"""File handling utilities."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic_settings import BaseSettings

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class FileHandlerSettings(BaseSettings):
    """Settings for file handler."""

    output_dir: str = "./outputs"

    class Config:
        env_file = ".env"
        env_prefix = ""
        extra = "ignore"  # Игнорировать дополнительные поля


def ensure_output_dir() -> Path:
    """
    Создает директорию для выходных файлов если её нет.

    Returns:
        Path к директории outputs
    """
    settings = FileHandlerSettings()
    output_path = Path(settings.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def save_output(
    data: Dict[str, Any],
    filename: Optional[str] = None,
    format: str = "json",
) -> Path:
    """
    Сохраняет сгенерированный контент в файл.

    Args:
        data: Данные для сохранения
        filename: Имя файла (если не указано, генерируется с timestamp)
        format: Формат файла (json или txt)

    Returns:
        Path к сохраненному файлу
    """
    output_dir = ensure_output_dir()

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"output_{timestamp}"

    filepath = output_dir / f"{filename}.{format}"

    try:
        if format == "json":
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        elif format == "txt":
            with open(filepath, "w", encoding="utf-8") as f:
                for key, value in data.items():
                    f.write(f"=== {key.upper()} ===\n\n")
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            f.write(f"{sub_key}: {sub_value}\n\n")
                    else:
                        f.write(f"{value}\n\n")
                    f.write("\n")

        logger.info(f"Файл сохранен: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Ошибка при сохранении файла: {e}")
        raise

