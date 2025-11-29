# Настройка OpenRouter.ai

## Быстрая настройка

1. **Создайте файл `.env`** в корне проекта:
```bash
cp env.example .env
```

2. **Файл `.env` уже содержит ваш API ключ OpenRouter:**
```env
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=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
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-4o
```

3. **Готово!** Теперь можно использовать:

```bash
# CLI
python -m src.cli --input "Ваша новость" --format telegram --pretty

# Web интерфейс
uvicorn src.main:app --reload
# Откройте http://localhost:8000
```

## Смена модели

Отредактируйте `OPENROUTER_MODEL` в `.env`:

```env
# GPT-4o (текущая)
OPENROUTER_MODEL=openai/gpt-4o

# Claude 3.5 Sonnet
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Gemini Pro
OPENROUTER_MODEL=google/gemini-pro

# Llama 3.1
OPENROUTER_MODEL=meta-llama/llama-3.1-70b-instruct
```

Полный список моделей: https://openrouter.ai/models

## Проверка работы

```bash
python -m src.cli --input "Тест" --format telegram
```

Если всё настроено правильно, вы увидите сгенерированный Telegram пост.

## Дополнительная информация

См. `OPENROUTER.md` для подробной информации о возможностях OpenRouter.

