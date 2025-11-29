# Архитектура проекта

## Обзор

Проект построен на модульной архитектуре с четким разделением ответственности между компонентами.

## Основная логика (псевдокод)

```
ФУНКЦИЯ generate_content(input_text, formats):
    результаты = {}
    
    ДЛЯ каждого формата В formats:
        ПОПЫТКА:
            загрузчик_промптов = PromptLoader()
            промпт_конфиг = загрузчик_промптов.get_prompt(формат)
            
            ai_провайдер = get_ai_provider()  // OpenAI или Ollama
            
            системный_промпт = промпт_конфиг["system"]
            пользовательский_промпт = промпт_конфиг["user"].format(input_text)
            
            генератор = get_generator(формат)  // TelegramGenerator, EmailGenerator, и т.д.
            контент = генератор.generate(input_text)
            
            контент = генератор.post_process(контент)  // Валидация и форматирование
            
            результаты[формат] = контент
            
        ИСКЛЮЧЕНИЕ:
            результаты[формат] = None
            логировать_ошибку(формат, ошибка)
    
    сохранить_в_файл(результаты)
    ВЕРНУТЬ результаты
КОНЕЦ ФУНКЦИИ
```

## Компоненты системы

### 1. AI Provider Layer (`src/ai/`)

**Назначение**: Абстракция для работы с различными AI провайдерами

**Компоненты**:
- `provider.py`: Базовый класс `AIProvider` и реализации
  - `OpenAIProvider`: Интеграция с OpenAI API
  - `OpenRouterProvider`: Интеграция с OpenRouter.ai (300+ моделей)
  - `OllamaProvider`: Интеграция с локальным Ollama
  - `get_ai_provider()`: Фабричная функция

**Принципы**:
- Абстракция через базовый класс позволяет легко добавлять новые провайдеры
- Настройки через переменные окружения
- Единый интерфейс `generate(system_prompt, user_prompt, temperature, max_tokens)`

### 2. Configuration Layer (`src/config/`)

**Назначение**: Управление промптами и конфигурацией

**Компоненты**:
- `prompts.yaml`: YAML файл с промптами для каждого формата
- `prompt_loader.py`: Загрузчик и кэширование промптов

**Структура промпта**:
```yaml
format_name:
  system: "Системный промпт с инструкциями для AI"
  user: "Шаблон пользовательского промпта с {input_text}"
```

### 3. Generator Layer (`src/generators/`)

**Назначение**: Генерация контента в различных форматах

**Компоненты**:
- `base.py`: Базовый класс `BaseGenerator`
- `formats.py`: Конкретные реализации генераторов
  - `TelegramGenerator`
  - `EmailGenerator`
  - `OfficialLetterGenerator`
  - `NewsletterGenerator`

**Жизненный цикл генерации**:
1. Загрузка промпта из конфигурации
2. Форматирование промпта с входным текстом
3. Вызов AI провайдера
4. Постобработка результата (валидация, форматирование)

**Расширяемость**:
```python
class NewFormatGenerator(BaseGenerator):
    format_name = "new_format"
    
    def get_temperature(self) -> float:
        return 0.7
    
    def post_process(self, content: str) -> str:
        # Кастомная обработка
        return content
```

### 4. API Layer (`src/main.py`)

**Назначение**: REST API для веб-интеграции

**Эндпоинты**:
- `GET /`: Веб-форма
- `POST /generate`: Генерация контента
- `GET /formats`: Список доступных форматов
- `GET /health`: Проверка здоровья сервиса

**Модели данных**:
- `GenerateRequest`: Входные данные (input_text, formats)
- `GenerateResponse`: Результаты генерации

### 5. CLI Layer (`src/cli.py`)

**Назначение**: Командная строка для локального использования

**Функциональность**:
- Парсинг аргументов через Click
- Генерация контента
- Красивый вывод (`--pretty`)
- Сохранение в файл (`--output`)

### 6. Utilities (`src/utils/`)

**Назначение**: Вспомогательные функции

**Компоненты**:
- `logger.py`: Настройка логирования
- `file_handler.py`: Сохранение результатов в файлы

## Поток данных

```
[Входной текст]
    ↓
[CLI/API/Web Form]
    ↓
[GenerateRequest]
    ↓
[Для каждого формата]
    ↓
[PromptLoader] → [Промпт из YAML]
    ↓
[BaseGenerator] → [AI Provider]
    ↓
[AI API] → [Сгенерированный контент]
    ↓
[Post-processing] → [Валидация и форматирование]
    ↓
[FileHandler] → [Сохранение в outputs/]
    ↓
[GenerateResponse] → [JSON ответ]
```

## Расширение системы

### Добавление нового формата

1. **Добавить промпт в `prompts.yaml`**:
```yaml
new_format:
  system: "Инструкции для AI..."
  user: "Шаблон с {input_text}"
```

2. **Создать генератор**:
```python
class NewFormatGenerator(BaseGenerator):
    format_name = "new_format"
    # Переопределить методы при необходимости
```

3. **Зарегистрировать в `formats.py`**:
```python
GENERATORS["new_format"] = NewFormatGenerator
```

### Добавление нового AI провайдера

1. **Создать класс провайдера**:
```python
class NewAIProvider(AIProvider):
    def generate(self, system_prompt, user_prompt, ...):
        # Реализация
```

2. **Добавить настройки в AISettings**:
```python
new_provider_api_key: Optional[str] = None
new_provider_base_url: str = "https://api.example.com"
```

3. **Добавить в фабрику**:
```python
def get_ai_provider():
    if provider == "new_provider":
        return NewAIProvider()
```

**Пример: OpenRouter**
OpenRouter полностью совместим с OpenAI API, поэтому использует тот же клиент с другим `base_url` и `api_key`.

## Обработка ошибок

- **AI Provider ошибки**: Логируются и пробрасываются наверх
- **Генератор ошибки**: Формат помечается как `None` в результатах
- **Валидация**: Проверка длины, структуры в `post_process()`
- **Файловые операции**: Try-catch с логированием

## Производительность

- **Кэширование промптов**: Промпты загружаются один раз
- **Параллелизация**: Можно добавить асинхронную генерацию для нескольких форматов
- **Таймауты**: Настроены для Ollama (60 сек)

## Безопасность

- **API ключи**: Хранятся в переменных окружения
- **Валидация входных данных**: Pydantic модели
- **Санитизация**: Экранирование HTML в веб-форме

