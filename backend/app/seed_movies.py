"""
Скрипт для заполнения базы данных тестовыми данными фильмов
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

from .database import AsyncSessionLocal, engine
from .models import Base, Movie
from .schemas import MovieCreate

# Тестовые данные фильмов
test_movies = [
    {
        "title": "Титаник",
        "year": 1997,
        "image_url": "https://example.com/titanic.jpg",
        "thumbnail_url": "https://example.com/titanic_thumb.jpg",
        "views": 1200000,
        "source_url": "https://example.com/movie/1",
        "duration": "3:14:00",
        "description": "Романтическая катастрофа о любви на фоне трагедии",
        "genre": "Драма",
        "rating": 7.8
    },
    {
        "title": "Криминальное чтиво",
        "year": 1994,
        "image_url": "https://example.com/pulp_fiction.jpg",
        "thumbnail_url": "https://example.com/pulp_fiction_thumb.jpg",
        "views": 950000,
        "source_url": "https://example.com/movie/2",
        "duration": "2:34:00",
        "description": "Необычный взгляд на криминальную жизнь Лос-Анджелеса",
        "genre": "Криминал",
        "rating": 8.9
    },
    {
        "title": "Форрест Гамп",
        "year": 1994,
        "image_url": "https://example.com/forest_gump.jpg",
        "thumbnail_url": "https://example.com/forest_gump_thumb.jpg",
        "views": 15000,
        "source_url": "https://example.com/movie/3",
        "duration": "2:22:00",
        "description": "История жизни человека с необычной судьбой",
        "genre": "Драма",
        "rating": 8.8
    },
    {
        "title": "Начало",
        "year": 2010,
        "image_url": "https://example.com/inception.jpg",
        "thumbnail_url": "https://example.com/inception_thumb.jpg",
        "views": 800,
        "source_url": "https://example.com/movie/4",
        "duration": "2:28:00",
        "description": "Фильм о мире снов и подсознания",
        "genre": "Фантастика",
        "rating": 8.2
    },
    {
        "title": "Матрица",
        "year": 1999,
        "image_url": "https://example.com/matrix.jpg",
        "thumbnail_url": "https://example.com/matrix_thumb.jpg",
        "views": 210000,
        "source_url": "https://example.com/movie/5",
        "duration": "2:16:00",
        "description": "Фильм о реальности и виртуальном мире",
        "genre": "Фантастика",
        "rating": 8.7
    }
]

async def create_test_movies():
    """Создание тестовых данных фильмов"""
    async with AsyncSessionLocal() as db:
        # Проверяем, есть ли уже фильмы в базе
        existing_count = await db.execute(
            "SELECT COUNT(*) FROM movies"
        )
        result = existing_count.fetchone()
        
        if result[0] > 0:
            print("Тестовые данные уже существуют в базе")
            return
        
        for movie_data in test_movies:
            movie = Movie(**movie_data)
            db.add(movie)
        
        await db.commit()
        print(f"Создано {len(test_movies)} тестовых фильмов")

if __name__ == "__main__":
    asyncio.run(create_test_movies())