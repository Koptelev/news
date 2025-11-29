# Быстрый старт

## 1. Установка (5 минут)

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd serv

# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate  # Windows

# Установите зависимости
pip install -r requirements.txt

# Настройте переменные окружения
# Создайте .env файл со следующим содержимым:
# AI_PROVIDER=openrouter
# OPENROUTER_API_KEY=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
# OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
# OPENROUTER_MODEL=openai/gpt-4o
```

## 2. Первый запуск

### Вариант A: CLI
```bash
python -m src.cli --input "Ваша новость здесь" --format telegram --pretty
```

### Вариант B: Web интерфейс
```bash
uvicorn src.main:app --reload
# Откройте http://localhost:8000
```

### Вариант C: API
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"input_text": "Ваша новость", "formats": ["telegram"]}'
```

## 3. Примеры

См. файл `EXAMPLES.md` для подробных примеров использования.

## 4. Использование OpenRouter (рекомендуется)

Проект настроен для использования OpenRouter.ai - унифицированного интерфейса для доступа к 300+ моделям.

**Текущая конфигурация:**
- Провайдер: OpenRouter
- API ключ: уже настроен в `.env`
- Модель: `openai/gpt-4o`

**Смена модели:**
Отредактируйте `.env` и измените `OPENROUTER_MODEL`:
- `openai/gpt-4o` - GPT-4o
- `anthropic/claude-3.5-sonnet` - Claude 3.5
- `google/gemini-pro` - Gemini Pro
- `meta-llama/llama-3.1-70b-instruct` - Llama 3.1

См. `OPENROUTER.md` для подробной информации.

## 5. Использование с Ollama (локально)

```bash
# Установите Ollama
# https://ollama.ai

# Запустите Ollama
ollama serve
ollama pull llama3.2

# Настройте .env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Используйте как обычно
python -m src.cli --input "Текст" --format telegram
```

## Структура проекта

```
serv/
├── src/              # Исходный код
│   ├── main.py       # FastAPI приложение
│   ├── cli.py        # CLI интерфейс
│   ├── ai/           # AI провайдеры
│   ├── generators/   # Генераторы форматов
│   ├── config/       # Конфигурация промптов
│   └── utils/        # Утилиты
├── templates/        # HTML шаблоны
├── outputs/          # Сгенерированные файлы (создается автоматически)
└── README.md         # Полная документация
```

## Следующие шаги

1. Прочитайте `README.md` для полной документации
2. Изучите `ARCHITECTURE.md` для понимания архитектуры
3. Посмотрите `EXAMPLES.md` для примеров
4. Настройте промпты в `src/config/prompts.yaml` под свои нужды

## Поддержка

Создайте Issue в GitHub для вопросов и предложений.

