"""Загрузка и управление промптами из конфигурации."""

from pathlib import Path
from typing import Dict, Optional

import yaml

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class PromptLoader:
    """Загрузчик промптов из YAML конфигурации."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Инициализация загрузчика промптов.

        Args:
            config_path: Путь к файлу с промптами (по умолчанию prompts.yaml)
        """
        if config_path is None:
            config_path = Path(__file__).parent / "prompts.yaml"
        self.config_path = config_path
        self._prompts: Optional[Dict] = None

    def load(self) -> Dict:
        """
        Загружает промпты из YAML файла.

        Returns:
            Словарь с промптами для каждого формата

        Raises:
            FileNotFoundError: Если файл конфигурации не найден
            yaml.YAMLError: Если файл содержит невалидный YAML
        """
        if self._prompts is not None:
            return self._prompts

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._prompts = yaml.safe_load(f)
            logger.info(f"Промпты загружены из {self.config_path}")
            return self._prompts
        except FileNotFoundError:
            logger.error(f"Файл конфигурации не найден: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Ошибка при парсинге YAML: {e}")
            raise

    def get_prompt(self, format_name: str) -> Dict[str, str]:
        """
        Получает промпт для конкретного формата.

        Args:
            format_name: Название формата (telegram, email, и т.д.)

        Returns:
            Словарь с ключами 'system' и 'user'

        Raises:
            KeyError: Если формат не найден в конфигурации
        """
        prompts = self.load()
        if format_name not in prompts:
            available = ", ".join(prompts.keys())
            raise KeyError(
                f"Формат '{format_name}' не найден. Доступные форматы: {available}"
            )
        return prompts[format_name]

    def list_formats(self) -> list[str]:
        """
        Возвращает список доступных форматов.

        Returns:
            Список названий форматов
        """
        prompts = self.load()
        return list(prompts.keys())

    def save_prompt(self, format_name: str, system_prompt: str, user_prompt: str) -> None:
        """
        Сохраняет или обновляет промпт для формата.

        Args:
            format_name: Название формата
            system_prompt: Системный промпт
            user_prompt: Пользовательский промпт
        """
        prompts = self.load()
        prompts[format_name] = {
            "system": system_prompt,
            "user": user_prompt,
        }
        
        # Сбрасываем кэш
        self._prompts = None
        
        # Сохраняем в файл
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(prompts, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            logger.info(f"Промпт для формата '{format_name}' сохранен")
        except Exception as e:
            logger.error(f"Ошибка при сохранении промпта: {e}")
            raise

    def delete_prompt(self, format_name: str) -> None:
        """
        Удаляет промпт для формата.

        Args:
            format_name: Название формата для удаления
        """
        prompts = self.load()
        if format_name in prompts:
            del prompts[format_name]
            self._prompts = None
            
            try:
                with open(self.config_path, "w", encoding="utf-8") as f:
                    yaml.dump(prompts, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
                logger.info(f"Промпт для формата '{format_name}' удален")
            except Exception as e:
                logger.error(f"Ошибка при удалении промпта: {e}")
                raise
        else:
            raise KeyError(f"Формат '{format_name}' не найден")

