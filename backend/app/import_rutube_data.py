"""
Скрипт для импорта данных из rutube_videos.db в основную таблицу movies
"""
import asyncio
import sqlite3
import os
from typing import List, Dict
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from .database import AsyncSessionLocal
from .models import Movie
from .schemas import MovieCreate


def get_rutube_videos_data(db_path: str = "backend/data/rutube_videos.db") -> List[Dict]:
    """
    Извлечение данных из rutube_videos.db
    """
    if not os.path.exists(db_path):
        print(f"База данных {db_path} не найдена")
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Получаем все видео из базы
    cursor.execute("""
        SELECT 
            id,
            title,
            url,
            thumbnail_url,
            duration,
            views,
            publication_date_text,
            source_name,
            scraped_at
        FROM videos
        WHERE source_name IS NOT NULL
    """)
    
    rows = cursor.fetchall()
    
    # Преобразуем в список словарей
    videos = []
    for row in rows:
        video = {
            'external_id': row[0],
            'title': row[1],
            'source_url': row[2],
            'thumbnail_url': row[3],
            'duration': row[4],
            'views': row[5],
            'publication_date_text': row[6],
            'source_name': row[7],
            'scraped_at': row[8]
        }
        
        # Пытаемся извлечь год из publication_date_text или scraped_at
        year = extract_year(video['publication_date_text'] or video['scraped_at'])
        
        # Преобразуем строку просмотров в число
        views_count = parse_views(video['views'])
        
        videos.append({
            'title': video['title'],
            'year': year,
            'image_url': video['thumbnail_url'],  # используем thumbnail как основное изображение
            'thumbnail_url': video['thumbnail_url'],
            'views': views_count,
            'added_at': datetime.now(),
            'source_url': video['source_url'],
            'duration': video['duration'],
            'description': f"Видео с {video['source_name']}",
            'genre': "Видео",  # по умолчанию
            'rating': None,  # пока нет рейтинга
            'is_active': True
        })
    
    conn.close()
    return videos


def extract_year(date_str: str) -> int:
    """
    Извлечение года из строки даты
    """
    if not date_str:
        return datetime.now().year
    
    # Пробуем разные форматы дат
    possible_formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d.%m.%Y",
        "%Y"
    ]
    
    for fmt in possible_formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.year
        except ValueError:
            continue
    
    # Если не удалось распознать, возвращаем текущий год
    return datetime.now().year


def parse_views(views_str: str) -> int:
    """
    Преобразование строки просмотров в число
    """
    if not views_str:
        return 0
    
    # Убираем лишние символы и пробуем преобразовать
    views_str = str(views_str).replace(' ', '').replace(',', '').lower()
    
    # Обрабатываем сокращенные обозначения
    if 'тыс' in views_str or 'k' in views_str:
        # Убираем 'тыс' или 'k' и умножаем на 100
        num_str = ''.join(filter(lambda x: x.isdigit() or x == '.', views_str))
        try:
            num = float(num_str)
            return int(num * 100)
        except ValueError:
            return 0
    elif 'млн' in views_str or 'm' in views_str:
        # Убираем 'млн' или 'm' и умножаем на 1000000
        num_str = ''.join(filter(lambda x: x.isdigit() or x == '.', views_str))
        try:
            num = float(num_str)
            return int(num * 100000)
        except ValueError:
            return 0
    else:
        # Просто число
        num_str = ''.join(filter(str.isdigit, views_str))
        try:
            return int(num_str)
        except ValueError:
            return 0


async def import_rutube_data_to_movies():
    """
    Импорт данных из rutube_videos.db в таблицу movies
    """
    # Получаем данные из rutube_videos.db
    rutube_videos = get_rutube_videos_data()
    
    if not rutube_videos:
        print("Нет данных для импорта из rutube_videos.db")
        return
    
    print(f"Найдено {len(rutube_videos)} видео для импорта")
    
    async with AsyncSessionLocal() as db:
        # Проверяем, есть ли уже фильмы с такими source_url
        existing_source_urls = []
        for video in rutube_videos:
            existing_movie = await db.execute(
                "SELECT id FROM movies WHERE source_url = :source_url",
                {"source_url": video['source_url']}
            )
            result = existing_movie.fetchone()
            if result:
                existing_source_urls.append(video['source_url'])
        
        # Фильтруем видео, которые уже существуют
        new_videos = [v for v in rutube_videos if v['source_url'] not in existing_source_urls]
        
        print(f"Новых видео для импорта: {len(new_videos)}")
        
        if not new_videos:
            print("Все видео из rutube_videos.db уже существуют в базе")
            return
        
        # Добавляем новые видео в таблицу movies
        for video in new_videos:
            movie = Movie(**video)
            db.add(movie)
        
        await db.commit()
        print(f"Импортировано {len(new_videos)} новых видео из rutube_videos.db")


if __name__ == "__main__":
    asyncio.run(import_rutube_data_to_movies())