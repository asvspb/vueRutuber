# backend/app

Основной код FastAPI приложения.

## Файлы

| Файл | Описание |
|------|----------|
| `main.py` | FastAPI app, роуты, lifespan events, background tasks |
| `models.py` | SQLAlchemy модели: Movie |
| `schemas.py` | Pydantic схемы для валидации |
| `crud.py` | CRUD операции для Movie |
| `database.py` | Async PostgreSQL (asyncpg) конфигурация |
| `rutube_api_scraper.py` | Скрапер Rutube API (aiohttp) |

## Модель Movie

```python
class Movie:
    id: int
    title: str
    year: int
    thumbnail_url: str
    views: int
    duration: str          # формат "HH:MM:SS"
    genre: str
    description: str
    source_url: str
    added_at: datetime
    is_active: bool
```