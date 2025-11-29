# Настройка OpenRouter.ai

[OpenRouter.ai](https://openrouter.ai/) - это унифицированный интерфейс для доступа к более чем 300 моделям от различных провайдеров через единый API.

## Преимущества

- ✅ **Доступ к множеству моделей** - OpenAI, Anthropic, Google, Meta, Mistral и др.
- ✅ **Лучшие цены** - конкурентные тарифы
- ✅ **Высокая доступность** - автоматический fallback при недоступности провайдера
- ✅ **OpenAI-совместимый API** - работает с существующим кодом без изменений
- ✅ **Единый интерфейс** - один API ключ для всех моделей

## Быстрая настройка

1. Получите API ключ на https://openrouter.ai/keys

2. Настройте `.env`:
```env
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=x-ai/grok-4.1-fast:free
```

3. Готово! Используйте как обычно:
```bash
python -m src.cli --input "Ваш текст" --format telegram
```

## Используемая модель

### xAI Grok (текущая)
- `x-ai/grok-4.1-fast:free` - **Бесплатная быстрая модель от xAI** ⭐

## Другие популярные модели

### OpenAI
- `openai/gpt-4o` - Самый мощный GPT-4
- `openai/gpt-4-turbo` - Быстрая версия GPT-4
- `openai/gpt-3.5-turbo` - Экономичная модель

### Anthropic
- `anthropic/claude-3.5-sonnet` - Claude 3.5 Sonnet
- `anthropic/claude-3-opus` - Claude 3 Opus
- `anthropic/claude-3-haiku` - Быстрая Claude 3

### Google
- `google/gemini-pro` - Gemini Pro
- `google/gemini-pro-vision` - Gemini с поддержкой изображений

### Meta
- `meta-llama/llama-3.1-70b-instruct` - Llama 3.1 70B
- `meta-llama/llama-3.1-8b-instruct` - Llama 3.1 8B

### Другие
- `mistralai/mistral-large` - Mistral Large
- `deepseek/deepseek-chat` - DeepSeek Chat
- `qwen/qwen-2.5-72b-instruct` - Qwen 2.5

Полный список: https://openrouter.ai/models

## Примеры использования разных моделей

### Grok 4.1 Fast (текущая, бесплатная)
```env
OPENROUTER_MODEL=x-ai/grok-4.1-fast:free
```

### GPT-4o
```env
OPENROUTER_MODEL=openai/gpt-4o
```

### Claude 3.5 Sonnet
```env
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
```

### Gemini Pro
```env
OPENROUTER_MODEL=google/gemini-pro
```

### Llama 3.1
```env
OPENROUTER_MODEL=meta-llama/llama-3.1-70b-instruct
```

## Стоимость

OpenRouter предлагает конкурентные цены. Проверьте актуальные тарифы на https://openrouter.ai/models

## Дополнительная информация

- Документация: https://openrouter.ai/docs
- Статус: https://openrouter.ai/status
- Поддержка: https://openrouter.ai/support

