"""CLI интерфейс для генерации контента."""

import json
import sys
from pathlib import Path
from typing import Optional

import click

from src.generators.formats import GENERATORS, get_generator
from src.utils.file_handler import save_output
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@click.command()
@click.option(
    "--input",
    "-i",
    "input_text",
    required=True,
    help="Входной текст для генерации контента",
)
@click.option(
    "--format",
    "-f",
    "formats",
    multiple=True,
    default=list(GENERATORS.keys()),
    help="Форматы для генерации (можно указать несколько раз)",
)
@click.option(
    "--output",
    "-o",
    "output_file",
    type=click.Path(),
    help="Путь к файлу для сохранения результатов (JSON)",
)
@click.option(
    "--pretty",
    "-p",
    is_flag=True,
    help="Красивый вывод в консоль",
)
def generate(
    input_text: str,
    formats: tuple,
    output_file: Optional[str],
    pretty: bool,
):
    """
    Генерирует контент в различных форматах на основе входного текста.

    Примеры:
        python -m src.cli --input "Ваша новость здесь"
        python -m src.cli --input "Текст" --format telegram --format email
        python -m src.cli --input "Текст" --output result.json
    """
    formats_list = list(formats) if formats else list(GENERATORS.keys())

    # Проверяем валидность форматов
    invalid_formats = [f for f in formats_list if f not in GENERATORS]
    if invalid_formats:
        click.echo(
            f"Ошибка: Неподдерживаемые форматы: {', '.join(invalid_formats)}",
            err=True,
        )
        click.echo(f"Доступные форматы: {', '.join(GENERATORS.keys())}", err=True)
        sys.exit(1)

    click.echo(f"Генерация контента для {len(formats_list)} форматов...")
    click.echo(f"Входной текст: {input_text[:100]}...\n")

    results = {}
    errors = {}

    for format_name in formats_list:
        try:
            click.echo(f"Генерация формата '{format_name}'...", nl=False)
            generator = get_generator(format_name)
            content = generator.generate(input_text)
            results[format_name] = content
            click.echo(" ✓")

            if pretty:
                click.echo(f"\n{'='*60}")
                click.echo(f"ФОРМАТ: {format_name.upper()}")
                click.echo(f"{'='*60}")
                click.echo(content)
                click.echo(f"{'='*60}\n")

        except Exception as e:
            click.echo(f" ✗ Ошибка: {e}", err=True)
            errors[format_name] = str(e)
            results[format_name] = None

    # Формируем итоговые данные
    output_data = {
        "input_text": input_text,
        "formats": formats_list,
        "results": results,
        "errors": errors if errors else None,
    }

    # Сохраняем в файл если указан
    if output_file:
        try:
            output_path = save_output(output_data, filename=Path(output_file).stem)
            click.echo(f"\nРезультаты сохранены в: {output_path}")
        except Exception as e:
            click.echo(f"Ошибка при сохранении файла: {e}", err=True)
    else:
        # Автоматически сохраняем в outputs/
        try:
            output_path = save_output(output_data)
            click.echo(f"\nРезультаты автоматически сохранены в: {output_path}")
        except Exception as e:
            click.echo(f"Предупреждение: не удалось сохранить файл: {e}", err=True)

    # Выводим JSON если не pretty режим
    if not pretty and not output_file:
        click.echo("\n" + json.dumps(output_data, ensure_ascii=False, indent=2))

    # Проверяем наличие ошибок
    if errors:
        click.echo(f"\nПредупреждение: {len(errors)} форматов не удалось сгенерировать")
        sys.exit(1)


if __name__ == "__main__":
    generate()

