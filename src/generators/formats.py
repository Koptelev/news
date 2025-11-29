"""Генераторы для различных форматов контента."""

import re
from typing import Optional

from src.generators.base import BaseGenerator
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class TelegramGenerator(BaseGenerator):
    """Генератор для Telegram постов."""

    format_name = "telegram"

    def get_temperature(self) -> float:
        """Более высокая температура для креативности."""
        return 0.8

    def get_max_tokens(self) -> Optional[int]:
        """Ограничение для коротких постов."""
        return 200

    def post_process(self, content: str) -> str:
        """Проверка длины и форматирование."""
        # Удаляем лишние пробелы и переносы
        content = re.sub(r"\n{3,}", "\n\n", content)
        content = content.strip()

        # Проверяем длину (макс 300 символов)
        if len(content) > 300:
            logger.warning(
                f"Telegram пост превышает 300 символов ({len(content)}). Обрезаем."
            )
            # Пытаемся обрезать по последнему предложению
            sentences = re.split(r"[.!?]\s+", content)
            result = ""
            for sentence in sentences:
                if len(result + sentence) <= 300:
                    result += sentence + ". "
                else:
                    break
            content = result.strip()[:300]

        return content


class EmailGenerator(BaseGenerator):
    """Генератор для email сообщений."""

    format_name = "email"

    def get_temperature(self) -> float:
        """Средняя температура для баланса креативности и структуры."""
        return 0.7

    def get_max_tokens(self) -> Optional[int]:
        """Ограничение для ~150 слов."""
        return 300

    def post_process(self, content: str) -> str:
        """Парсинг темы и тела из ответа."""
        # Пытаемся извлечь тему и тело из структурированного ответа
        if "ТЕМА:" in content or "Тема:" in content:
            # Формат уже структурирован
            return content.strip()

        # Если формат не структурирован, пытаемся улучшить
        lines = content.split("\n")
        if len(lines) > 1:
            # Первая строка может быть темой
            return content.strip()

        return content.strip()


class OfficialLetterGenerator(BaseGenerator):
    """Генератор для официальных писем."""

    format_name = "official_letter"

    def get_temperature(self) -> float:
        """Низкая температура для формальности."""
        return 0.5

    def get_max_tokens(self) -> Optional[int]:
        """Ограничение для ~300 слов."""
        return 600

    def post_process(self, content: str) -> str:
        """Проверка структуры официального письма."""
        # Убеждаемся, что есть плейсхолдеры
        if "[ОТПРАВИТЕЛЬ]" not in content:
            logger.warning("Плейсхолдер [ОТПРАВИТЕЛЬ] не найден в письме")
        if "[ПОЛУЧАТЕЛЬ]" not in content:
            logger.warning("Плейсхолдер [ПОЛУЧАТЕЛЬ] не найден в письме")
        if "[ДАТА]" not in content:
            logger.warning("Плейсхолдер [ДАТА] не найден в письме")

        return content.strip()


class NewsletterGenerator(BaseGenerator):
    """Генератор для массовых рассылок."""

    format_name = "newsletter"

    def get_temperature(self) -> float:
        """Средняя температура для дружелюбного тона."""
        return 0.7

    def get_max_tokens(self) -> Optional[int]:
        """Ограничение для ~250 слов."""
        return 500

    def post_process(self, content: str) -> str:
        """Улучшение читаемости рассылки."""
        # Удаляем лишние пустые строки
        content = re.sub(r"\n{3,}", "\n\n", content)
        return content.strip()


# Реестр генераторов
GENERATORS = {
    "telegram": TelegramGenerator,
    "email": EmailGenerator,
    "official_letter": OfficialLetterGenerator,
    "newsletter": NewsletterGenerator,
}


def get_generator(format_name: str) -> BaseGenerator:
    """
    Получает генератор для указанного формата.

    Args:
        format_name: Название формата

    Returns:
        Экземпляр генератора

    Raises:
        ValueError: Если формат не поддерживается
    """
    if format_name not in GENERATORS:
        available = ", ".join(GENERATORS.keys())
        raise ValueError(
            f"Формат '{format_name}' не поддерживается. Доступные: {available}"
        )
    return GENERATORS[format_name]()

