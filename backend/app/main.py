import asyncio
import os
from dotenv import load_dotenv
from typing import List

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from .database import get_db, engine
from .models import Base
from . import crud, schemas
from .rutube_api_scraper import run_api_scraper, import_rutube_playlist_videos, import_rutube_channel
import re
from urllib.parse import urlparse

# Загружаем переменные окружения из файла .env
load_dotenv()


# Настройки Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# Приложение FastAPI должно быть создано ДО регистрации обработчиков событий
app = FastAPI(title="VueExpert Backend", version="0.1.0")

# Создаем подприложение для API
api_router = APIRouter()


# Получаем разрешенные источники из переменной окружения
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:4173,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Клиент Redis
redis_client = redis.from_url(
    f"redis://{REDIS_HOST}:{REDIS_PORT}",
    encoding="utf-8",
    decode_responses=True,
)

# Создание таблиц при запуске приложения
# Планировщик ежедневного запуска Rutube скрапера

_scrape_task: asyncio.Task | None = None

async def _daily_scrape_loop():
    while True:
        try:
            # Запускаем скрапинг 100 элементов
            await run_api_scraper(limit=100)
        except Exception as e:  # noqa: BLE001
            print(f"[scraper] Error during scheduled run: {e}")
        # Ждём ~24 часа
        await asyncio.sleep(24 * 60 * 60)

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Запускаем фоновую задачу ежедневного скрапинга
    global _scrape_task
    loop = asyncio.get_event_loop()
    _scrape_task = loop.create_task(_daily_scrape_loop())

@app.on_event("shutdown")
async def shutdown_event():
    global _scrape_task
    if _scrape_task and not _scrape_task.done():
        _scrape_task.cancel()


@api_router.get("/health")
async def health() -> dict:
    """Простая проверка работы backend и подключения к Redis и PostgreSQL."""
    try:
        pong = await redis_client.ping()
        redis_status = "ok" if pong else "unreachable"
    except Exception as exc:  # noqa: BLE001
        redis_status = f"error: {exc}"

    try:
        # Проверим возможность подключения к PostgreSQL
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:  # noqa: BLE001
        db_status = f"error: {exc}"

    return {"status": "ok", "redis": redis_status, "database": db_status}


@api_router.get("/counter")
async def counter() -> dict:
    """Пример эндпоинта, который использует Redis для счётчика."""
    value = await redis_client.incr("counter")
    return {"counter": value}


# Эндпоинты для работы с SQLite
@api_router.post("/items/", response_model=schemas.Item)
async def create_item(item: schemas.ItemCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_item(db=db, item=item)


@api_router.get("/items/", response_model=List[schemas.Item])
async def read_items(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    items = await crud.get_items(db, skip=skip, limit=limit)
    return items


@api_router.get("/items/{item_id}", response_model=schemas.Item)
async def read_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await crud.get_item(db, item_id=item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@api_router.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_user(db=db, user=user)


@api_router.get("/users/", response_model=List[schemas.User])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    users = await crud.get_users(db, skip=skip, limit=limit)
    return users


# Ручной запуск скрапера
@api_router.post("/scrape/rutube")
async def trigger_rutube_scraper(limit: int = 100):
    try:
        count = await run_api_scraper(limit=limit)
        return {"status": "ok", "scraped": count}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Scraper error: {e}")

# Эндпоинты для работы с фильмами
@api_router.post("/movies/", response_model=schemas.Movie)
async def create_movie(movie: schemas.MovieCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_movie(db=db, movie=movie)


@api_router.get("/movies/", response_model=List[schemas.Movie])
async def read_movies(
    skip: int = 0, 
    limit: int = 10, 
    is_active: bool = True,
    db: AsyncSession = Depends(get_db)
):
    movies = await crud.get_movies(db, skip=skip, limit=limit, is_active=is_active)
    return movies


@api_router.get("/movies/{movie_id}", response_model=schemas.Movie)
async def read_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    movie = await crud.get_movie(db, movie_id=movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@api_router.put("/movies/{movie_id}", response_model=schemas.Movie)
async def update_movie(
    movie_id: int, 
    movie_update: schemas.MovieUpdate, 
    db: AsyncSession = Depends(get_db)
):
    updated_movie = await crud.update_movie(db, movie_id=movie_id, movie_update=movie_update)
    if updated_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return updated_movie


@api_router.delete("/movies/{movie_id}", response_model=schemas.Movie)
async def delete_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    deleted_movie = await crud.delete_movie(db, movie_id=movie_id)
    if deleted_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return deleted_movie


@api_router.get("/movies/year/{year}", response_model=List[schemas.Movie])
async def read_movies_by_year(
    year: int, 
    skip: int = 0, 
    limit: int = 10, 
    db: AsyncSession = Depends(get_db)
):
    movies = await crud.get_movies_by_year(db, year=year, skip=skip, limit=limit)
    return movies


@api_router.get("/movies/genre/{genre}", response_model=List[schemas.Movie])
async def read_movies_by_genre(
    genre: str, 
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    movies = await crud.get_movies_by_genre(db, genre=genre, skip=skip, limit=limit)
    return movies


@api_router.post("/movies/{movie_id}/increment-views")
async def increment_movie_views(movie_id: int, db: AsyncSession = Depends(get_db)):
    updated_movie = await crud.increment_movie_views(db, movie_id=movie_id)
    if updated_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"views": updated_movie.views}


# Эндпоинты для работы с каналами
@api_router.get("/channels/", response_model=List[schemas.ChannelWithVideosCount])
async def read_channels(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    channels = await crud.get_channels_with_videos_count(db, skip=skip, limit=limit)
    return channels


@api_router.get("/channels/{channel_id}", response_model=schemas.Channel)
async def read_channel(channel_id: int, db: AsyncSession = Depends(get_db)):
    channel = await crud.get_channel(db, channel_id=channel_id)
    if channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    return channel


# Эндпоинты для работы с плейлистами
@api_router.get("/playlists/", response_model=List[schemas.PlaylistWithVideosCount])
async def read_playlists(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    playlists = await crud.get_playlists_with_videos_count(db, skip=skip, limit=limit)
    return playlists


@api_router.get("/playlists/{playlist_id}", response_model=schemas.Playlist)
async def read_playlist(playlist_id: int, db: AsyncSession = Depends(get_db)):
    playlist = await crud.get_playlist(db, playlist_id=playlist_id)
    if playlist is None:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return playlist


@api_router.get("/playlists/{playlist_id}/videos", response_model=List[schemas.Movie])
async def read_playlist_videos(
    playlist_id: int,
    channel_id: int = None,
    skip: int = 0,
    limit: int = 24,
    order: str = "-channel_added_at",
    db: AsyncSession = Depends(get_db)
):
    """Получить видео из плейлиста с возможностью фильтрации по каналу и сортировки"""
    videos = await crud.get_playlist_movies_with_channel_filter(
        db,
        playlist_id=playlist_id,
        channel_id=channel_id,
        skip=skip,
        limit=limit,
        order_by=order
    )
    return videos


# Эндпоинты для импорта плейлистов из Rutube

def validate_rutube_playlist_url(url: str) -> bool:
    """Проверяет, является ли URL действительным URL плейлиста Rutube"""
    try:
        parsed = urlparse(url)
        # Проверяем домен
        if not parsed.netloc.endswith('rutube.ru'):
            return False

        # Проверяем путь - должен быть вида /plst/{id}/ или /plst/{id}
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) >= 2 and path_parts[0] == 'plst':
            playlist_id = path_parts[1]
            return playlist_id.isdigit()

        return False
    except Exception:
        return False


def extract_playlist_id_from_url(url: str) -> str:
    """Извлекает ID плейлиста из URL"""
    # Пример URL: https://rutube.ru/plst/707635/
    match = re.search(r'/plst/(\d+)', url)
    if match:
        return match.group(1)
    return None


def validate_rutube_channel_url(url: str) -> bool:
    """Проверяет, что URL является валидным URL канала Rutube"""
    try:
        parsed = urlparse(url)
        if not parsed.netloc.endswith('rutube.ru'):
            return False
        path_parts = parsed.path.strip('/').split('/')
        # Ожидаем /channel/{id}/
        if len(path_parts) >= 2 and path_parts[0] == 'channel':
            ch_id = path_parts[1]
            return ch_id.isdigit()
        return False
    except Exception:
        return False


def extract_channel_id_from_url(url: str) -> str | None:
    """Извлекает ID канала из URL вида https://rutube.ru/channel/{id}/"""
    match = re.search(r'/channel/(\d+)', url)
    return match.group(1) if match else None


@api_router.post("/playlists/import")
async def import_playlist(
    rutube_playlist_url: str,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Импорт плейлиста из Rutube"""
    # Валидация URL
    if not validate_rutube_playlist_url(rutube_playlist_url):
        raise HTTPException(
            status_code=400,
            detail="Invalid Rutube playlist URL. Expected format: https://rutube.ru/plst/{id}/"
        )

    # Извлечение ID плейлиста
    playlist_id = extract_playlist_id_from_url(rutube_playlist_url)
    if not playlist_id:
        raise HTTPException(
            status_code=400,
            detail="Could not extract playlist ID from URL"
        )

    try:
        # Запуск импорта
        result = await import_rutube_playlist_videos(
            db,
            rutube_playlist_url,
            playlist_id,
            limit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import error: {str(e)}")


@api_router.post("/channels/import")
async def import_channel(
    rutube_channel_url: str,
    channel_videos_limit: int = 0,
    scan_playlists: bool = True,
    per_playlist_limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Импорт/создание канала по URL Rutube. Опционально импорт последних видео (import_limit > 0)."""
    if not validate_rutube_channel_url(rutube_channel_url):
        raise HTTPException(
            status_code=400,
            detail="Invalid Rutube channel URL. Expected format: https://rutube.ru/channel/{id}/"
        )

    channel_id = extract_channel_id_from_url(rutube_channel_url)
    if not channel_id:
        raise HTTPException(status_code=400, detail="Could not extract channel ID from URL")

    try:
        result = await import_rutube_channel(
            db,
            rutube_channel_url,
            channel_id,
            channel_videos_limit if channel_videos_limit and channel_videos_limit > 0 else None,
            scan_playlists,
            per_playlist_limit,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Channel import error: {str(e)}")

# Подключаем маршруты к основному приложению с префиксом /api и без префикса для совместимости тестов
app.include_router(api_router, prefix="/api")
app.include_router(api_router)  # duplicate mount at root for test expectations