"""Базовый класс для генераторов контента."""

from abc import ABC, abstractmethod
from typing import Dict, Optional

from src.ai.provider import AIProvider, get_ai_provider
from src.config.prompt_loader import PromptLoader
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseGenerator(ABC):
    """Базовый класс для генераторов различных форматов контента."""

    format_name: str = ""  # Должно быть переопределено в подклассах

    def __init__(
        self,
        ai_provider: Optional[AIProvider] = None,
        prompt_loader: Optional[PromptLoader] = None,
    ):
        """
        Инициализация генератора.

        Args:
            ai_provider: AI провайдер (если не указан, создается автоматически)
            prompt_loader: Загрузчик промптов (если не указан, создается автоматически)
        """
        self.ai_provider = ai_provider or get_ai_provider()
        self.prompt_loader = prompt_loader or PromptLoader()
        self._prompt_config: Optional[Dict[str, str]] = None

    @property
    def prompt_config(self) -> Dict[str, str]:
        """Загружает и кэширует конфигурацию промпта для формата."""
        if self._prompt_config is None:
            self._prompt_config = self.prompt_loader.get_prompt(self.format_name)
        return self._prompt_config

    def generate(self, input_text: str, **kwargs) -> str:
        """
        Генерирует контент в заданном формате.

        Args:
            input_text: Входной текст для обработки
            **kwargs: Дополнительные параметры для генерации

        Returns:
            Сгенерированный контент
        """
        logger.info(f"Генерация контента формата '{self.format_name}'")

        prompt_config = self.prompt_config
        system_prompt = prompt_config["system"]
        user_prompt = prompt_config["user"].format(input_text=input_text, **kwargs)

        try:
            result = self.ai_provider.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=self.get_temperature(),
                max_tokens=self.get_max_tokens(),
            )
            logger.info(f"Контент формата '{self.format_name}' успешно сгенерирован")
            return self.post_process(result)
        except Exception as e:
            logger.error(f"Ошибка при генерации контента формата '{self.format_name}': {e}")
            raise

    def get_temperature(self) -> float:
        """
        Возвращает температуру для генерации (может быть переопределено).

        Returns:
            Температура генерации (0.0-1.0)
        """
        return 0.7

    def get_max_tokens(self) -> Optional[int]:
        """
        Возвращает максимальное количество токенов (может быть переопределено).

        Returns:
            Максимальное количество токенов или None
        """
        return None

    def post_process(self, content: str) -> str:
        """
        Постобработка сгенерированного контента (может быть переопределено).

        Args:
            content: Сгенерированный контент

        Returns:
            Обработанный контент
        """
        return content.strip()

