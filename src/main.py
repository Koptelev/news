"""FastAPI приложение для генерации контента."""

from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.config.prompt_loader import PromptLoader
from src.generators.formats import GENERATORS, get_generator
from src.utils.file_handler import save_output
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI(
    title="Генератор контента",
    description="AI-сервис для автоматической генерации контента в различных форматах",
    version="0.1.0",
)


class GenerateRequest(BaseModel):
    """Модель запроса на генерацию."""

    input_text: str = Field(..., description="Входной текст для обработки")
    formats: List[str] = Field(
        default=["telegram", "email", "blog", "press_release"],
        description="Список форматов для генерации",
    )


class GenerateResponse(BaseModel):
    """Модель ответа с результатами генерации."""

    input_text: str
    formats: List[str]
    results: dict
    timestamp: str
    output_file: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница с веб-формой."""
    try:
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
            <head><title>Content Generator</title></head>
            <body>
                <h1>Content Multi-Format Generator</h1>
                <p>Веб-форма не найдена. Используйте API эндпоинт /generate</p>
                <p>Документация API: <a href="/docs">/docs</a></p>
            </body>
        </html>
        """


@app.post("/generate", response_model=GenerateResponse)
async def generate_content(request: GenerateRequest) -> GenerateResponse:
    """
    Генерирует контент в указанных форматах.

    Args:
        request: Запрос с входным текстом и списком форматов

    Returns:
        Ответ с сгенерированным контентом
    """
    logger.info(f"Получен запрос на генерацию форматов: {request.formats}")

    results = {}
    errors = {}

    for format_name in request.formats:
        try:
            generator = get_generator(format_name)
            content = generator.generate(request.input_text)
            results[format_name] = content
            logger.info(f"Формат '{format_name}' успешно сгенерирован")

        except Exception as e:
            logger.error(f"Ошибка при генерации формата '{format_name}': {e}")
            errors[format_name] = str(e)
            results[format_name] = None

    if not results or all(v is None for v in results.values()):
        raise HTTPException(
            status_code=500, detail="Не удалось сгенерировать ни один формат"
        )

    timestamp = datetime.now().isoformat()

    # Сохраняем результаты в файл
    output_data = {
        "input_text": request.input_text,
        "formats": request.formats,
        "results": results,
        "errors": errors if errors else None,
        "timestamp": timestamp,
    }

    try:
        output_file = save_output(output_data)
        output_file_str = str(output_file)
    except Exception as e:
        logger.warning(f"Не удалось сохранить файл: {e}")
        output_file_str = None

    response = GenerateResponse(
        input_text=request.input_text,
        formats=request.formats,
        results=results,
        timestamp=timestamp,
        output_file=output_file_str,
    )

    return response


@app.get("/formats")
async def list_formats():
    """Возвращает список доступных форматов."""
    loader = PromptLoader()
    all_formats = loader.list_formats()
    
    return {
        "available_formats": all_formats,
        "builtin_formats": list(GENERATORS.keys()),
        "custom_formats": [f for f in all_formats if f not in GENERATORS],
        "descriptions": {
            "telegram": "Короткий Telegram пост (макс 300 символов)",
            "email": "Email сообщение с темой и телом (~150 слов)",
            "official_letter": "Официальное письмо (~300 слов)",
            "newsletter": "Массовая рассылка (~250 слов)",
            "blog": "Информативная блог-статья (~400-500 слов)",
            "press_release": "Профессиональный пресс-релиз (~300-400 слов)",
            "announcement": "Корпоративное объявление (~200-300 слов)",
            "ad_copy": "Убедительный рекламный текст (~150-200 слов)",
            "seo_article": "SEO-оптимизированная статья (~500-700 слов)",
            "video_script": "Сценарий для видео (~300-400 слов)",
            "podcast_description": "Описание эпизода подкаста (~150-200 слов)",
            "faq": "Раздел часто задаваемых вопросов",
        },
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса."""
    return {"status": "ok", "service": "content-generator"}


# ========== Управление форматами ==========

class FormatRequest(BaseModel):
    """Модель запроса для создания/обновления формата."""

    format_name: str = Field(..., description="Название формата")
    system_prompt: str = Field(..., description="Системный промпт")
    user_prompt: str = Field(..., description="Пользовательский промпт (может содержать {input_text})")


@app.get("/formats/manage")
async def manage_formats_page():
    """Страница управления форматами."""
    try:
        with open("templates/manage_formats.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="""
            <html>
                <head><title>Управление форматами</title></head>
                <body>
                    <h1>Управление форматами</h1>
                    <p>Страница управления не найдена. Используйте API эндпоинты.</p>
                    <p><a href="/docs">Документация API</a></p>
                </body>
            </html>
            """
        )


@app.get("/api/formats")
async def get_all_formats():
    """Получить все форматы с их промптами."""
    loader = PromptLoader()
    formats = loader.load()
    
    result = {}
    for format_name, prompts in formats.items():
        result[format_name] = {
            "system": prompts.get("system", ""),
            "user": prompts.get("user", ""),
            "is_builtin": format_name in GENERATORS,
        }
    
    return result


@app.get("/api/formats/{format_name}")
async def get_format(format_name: str):
    """Получить промпты для конкретного формата."""
    loader = PromptLoader()
    try:
        prompts = loader.get_prompt(format_name)
        return {
            "format_name": format_name,
            "system": prompts["system"],
            "user": prompts["user"],
            "is_builtin": format_name in GENERATORS,
        }
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Формат '{format_name}' не найден")


@app.post("/api/formats")
async def create_or_update_format(request: FormatRequest):
    """Создать или обновить формат."""
    loader = PromptLoader()
    
    try:
        loader.save_prompt(
            format_name=request.format_name,
            system_prompt=request.system_prompt,
            user_prompt=request.user_prompt,
        )
        return {
            "message": f"Формат '{request.format_name}' успешно сохранен",
            "format_name": request.format_name,
        }
    except Exception as e:
        logger.error(f"Ошибка при сохранении формата: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/formats/{format_name}")
async def delete_format(format_name: str):
    """Удалить формат."""
    if format_name in GENERATORS:
        raise HTTPException(
            status_code=400,
            detail=f"Встроенный формат '{format_name}' нельзя удалить"
        )
    
    loader = PromptLoader()
    try:
        loader.delete_prompt(format_name)
        return {"message": f"Формат '{format_name}' успешно удален"}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Формат '{format_name}' не найден")
    except Exception as e:
        logger.error(f"Ошибка при удалении формата: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

