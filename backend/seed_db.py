"""
Скрипт для заполнения базы данных тестовыми данными
"""
import asyncio
import sys
import os

# Добавляем путь к backend для импорта модулей
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.seed_movies import create_test_movies
# Import обновленной функции импорта
from app.import_rutube_data import import_rutube_data_to_movies
from app.database import engine
from app.models import Base

async def main():
    # Создаем таблицы в базе данных
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Заполняем базу тестовыми данными фильмов
    await create_test_movies()

    # Импортируем данные из rutube_videos.db
    await import_rutube_data_to_movies()

if __name__ == "__main__":
    asyncio.run(main())