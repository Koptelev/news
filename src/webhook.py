"""GitHub webhook handler для автоматической обработки markdown файлов (опционально)."""

import json
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel

from src.generators.formats import GENERATORS, get_generator
from src.utils.file_handler import save_output
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Создаем отдельное приложение для webhook (можно интегрировать в main.py)
webhook_app = FastAPI(title="GitHub Webhook Handler")


class GitHubWebhookPayload(BaseModel):
    """Модель payload от GitHub webhook."""

    ref: Optional[str] = None
    commits: Optional[list] = None
    repository: Optional[Dict] = None


async def extract_markdown_content(file_path: str) -> Optional[str]:
    """
    Извлекает контент из markdown файла.

    Args:
        file_path: Путь к markdown файлу

    Returns:
        Содержимое файла или None
    """
    try:
        path = Path(file_path)
        if path.exists() and path.suffix == ".md":
            return path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {file_path}: {e}")
    return None


@webhook_app.post("/webhook/github")
async def github_webhook(request: Request):
    """
    Обработчик GitHub webhook для автоматической генерации контента.

    Ожидает webhook от GitHub с информацией о push в репозиторий.
    Ищет новые/измененные .md файлы и генерирует контент.

    Настройка в GitHub:
    1. Settings → Webhooks → Add webhook
    2. Payload URL: https://your-domain.com/webhook/github
    3. Content type: application/json
    4. Events: Just the push event
    """
    try:
        payload = await request.json()
        logger.info(f"Получен webhook от GitHub: {payload.get('ref', 'unknown')}")

        # Извлекаем информацию о коммитах
        commits = payload.get("commits", [])
        if not commits:
            return {"message": "Нет коммитов для обработки"}

        results = []

        for commit in commits:
            # Проверяем добавленные и измененные файлы
            added_files = commit.get("added", [])
            modified_files = commit.get("modified", [])

            for file_path in added_files + modified_files:
                if file_path.endswith(".md"):
                    logger.info(f"Обработка markdown файла: {file_path}")

                    # В реальном сценарии нужно клонировать/скачать файл из репозитория
                    # Здесь упрощенная версия - предполагаем что файл доступен локально
                    content = await extract_markdown_content(file_path)

                    if content:
                        # Генерируем контент для всех форматов
                        format_results = {}
                        for format_name in GENERATORS.keys():
                            try:
                                generator = get_generator(format_name)
                                generated = generator.generate(content)
                                format_results[format_name] = generated
                            except Exception as e:
                                logger.error(f"Ошибка генерации {format_name}: {e}")
                                format_results[format_name] = None

                        # Сохраняем результаты
                        output_data = {
                            "source_file": file_path,
                            "source_content": content,
                            "results": format_results,
                            "commit": commit.get("id"),
                        }

                        save_output(output_data, filename=f"webhook_{Path(file_path).stem}")
                        results.append({"file": file_path, "status": "processed"})

        return {
            "message": "Webhook обработан",
            "processed_files": len(results),
            "results": results,
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Невалидный JSON")
    except Exception as e:
        logger.error(f"Ошибка при обработке webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@webhook_app.get("/webhook/health")
async def webhook_health():
    """Проверка здоровья webhook сервиса."""
    return {"status": "ok", "service": "github-webhook"}


# Для использования, добавьте в main.py:
# from src.webhook import webhook_app
# app.mount("/webhook", webhook_app)

