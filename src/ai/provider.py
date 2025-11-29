"""Абстракция для AI провайдеров."""

from abc import ABC, abstractmethod
from typing import Dict, Optional

from pydantic_settings import BaseSettings

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class AISettings(BaseSettings):
    """Настройки AI провайдера."""

    ai_provider: str = "openai"
    openai_api_key: Optional[str] = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o"
    openrouter_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "x-ai/grok-4.1-fast:free"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    class Config:
        env_file = ".env"
        env_prefix = ""
        extra = "ignore"  # Игнорировать дополнительные поля


class AIProvider(ABC):
    """Абстрактный базовый класс для AI провайдеров."""

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Генерирует текст с использованием AI.

        Args:
            system_prompt: Системный промпт
            user_prompt: Пользовательский промпт
            temperature: Температура генерации (0.0-1.0)
            max_tokens: Максимальное количество токенов

        Returns:
            Сгенерированный текст
        """
        pass


class OpenAIProvider(AIProvider):
    """Провайдер для OpenAI API."""

    def __init__(self, settings: Optional[AISettings] = None):
        """
        Инициализация OpenAI провайдера.

        Args:
            settings: Настройки AI (если не указаны, загружаются из env)
        """
        self.settings = settings or AISettings()

        if not self.settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY не установлен. Установите переменную окружения."
            )

        try:
            from openai import OpenAI

            self.client = OpenAI(
                api_key=self.settings.openai_api_key,
                base_url=self.settings.openai_base_url,
            )
            logger.info(
                f"OpenAI провайдер инициализирован (модель: {self.settings.openai_model})"
            )
        except ImportError:
            raise ImportError(
                "Библиотека openai не установлена. Установите: pip install openai"
            )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Генерирует текст через OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Ошибка при генерации через OpenAI: {e}")
            raise


class OpenRouterProvider(AIProvider):
    """Провайдер для OpenRouter.ai (унифицированный интерфейс для LLM)."""

    def __init__(self, settings: Optional[AISettings] = None):
        """
        Инициализация OpenRouter провайдера.

        Args:
            settings: Настройки AI (если не указаны, загружаются из env)
        """
        self.settings = settings or AISettings()

        if not self.settings.openrouter_api_key:
            raise ValueError(
                "OPENROUTER_API_KEY не установлен. Установите переменную окружения."
            )

        try:
            from openai import OpenAI

            # OpenRouter полностью совместим с OpenAI API
            self.client = OpenAI(
                api_key=self.settings.openrouter_api_key,
                base_url=self.settings.openrouter_base_url,
            )
            logger.info(
                f"OpenRouter провайдер инициализирован (модель: {self.settings.openrouter_model})"
            )
        except ImportError:
            raise ImportError(
                "Библиотека openai не установлена. Установите: pip install openai"
            )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Генерирует текст через OpenRouter API."""
        try:
            response = self.client.chat.completions.create(
                model=self.settings.openrouter_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Ошибка при генерации через OpenRouter: {e}")
            raise


class OllamaProvider(AIProvider):
    """Провайдер для Ollama (локальный LLM)."""

    def __init__(self, settings: Optional[AISettings] = None):
        """
        Инициализация Ollama провайдера.

        Args:
            settings: Настройки AI (если не указаны, загружаются из env)
        """
        self.settings = settings or AISettings()
        self.base_url = self.settings.ollama_base_url
        self.model = self.settings.ollama_model

        try:
            import httpx

            self.client = httpx.Client(base_url=self.base_url, timeout=60.0)
            logger.info(
                f"Ollama провайдер инициализирован (модель: {self.model}, URL: {self.base_url})"
            )
        except ImportError:
            raise ImportError(
                "Библиотека httpx не установлена. Установите: pip install httpx"
            )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Генерирует текст через Ollama API."""
        try:
            # Ollama использует комбинированный промпт
            combined_prompt = f"{system_prompt}\n\n{user_prompt}"

            response = self.client.post(
                "/api/generate",
                json={
                    "model": self.model,
                    "prompt": combined_prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                },
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except Exception as e:
            logger.error(f"Ошибка при генерации через Ollama: {e}")
            raise


def get_ai_provider(settings: Optional[AISettings] = None) -> AIProvider:
    """
    Фабричная функция для получения AI провайдера.

    Args:
        settings: Настройки AI (если не указаны, загружаются из env)

    Returns:
        Экземпляр AI провайдера

    Raises:
        ValueError: Если провайдер не поддерживается
    """
    settings = settings or AISettings()
    provider_name = settings.ai_provider.lower()

    if provider_name == "openai":
        return OpenAIProvider(settings)
    elif provider_name == "openrouter":
        return OpenRouterProvider(settings)
    elif provider_name == "ollama":
        return OllamaProvider(settings)
    else:
        raise ValueError(
            f"Неподдерживаемый провайдер: {provider_name}. "
            f"Доступные: openai, openrouter, ollama"
        )

