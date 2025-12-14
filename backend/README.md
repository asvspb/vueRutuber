# Backend

FastAPI бэкенд для vueRutube с автоматическим сбором данных с Rutube API.

## Структура

```
backend/
├── app/
│   ├── main.py               # FastAPI приложение, роуты, background tasks
│   ├── models.py             # SQLAlchemy модели (Movie)
│   ├── schemas.py            # Pydantic схемы
│   ├── crud.py               # CRUD операции
│   ├── database.py           # Async PostgreSQL конфигурация
│   └── rutube_api_scraper.py # Rutube API скрапер (aiohttp)
├── tests/                    # Pytest тесты
├── Dockerfile                # Multi-stage build
├── pyproject.toml            # Poetry конфигурация
└── requirements.txt          # Pip зависимости
```

## API Endpoints

### Movies
- `GET /api/movies/` - список фильмов (пагинация: skip, limit)
- `GET /api/movies/{id}` - фильм по ID
- `GET /api/movies/year/{year}` - фильмы по году
- `GET /api/movies/genre/{genre}` - фильмы по жанру
- `POST /api/movies/` - создать фильм
- `PUT /api/movies/{id}` - обновить фильм
- `DELETE /api/movies/{id}` - удалить фильм

### Scraper
- `POST /api/scrape/rutube?limit=100` - запустить скрапер вручную

### Health
- `GET /api/health` - проверка статуса сервисов

## Rutube Scraper

Скрапер использует официальный Rutube API:

```python
# API endpoint
https://rutube.ru/api/video/person/{CHANNEL_ID}/?page=1&page_size=20

# Получаемые данные
- title, description
- thumbnail_url
- hits (просмотры)
- duration (секунды)
- category (жанр)
- created_ts (дата)
```

Автоматический запуск: **раз в 24 часа** (asyncio background task)

## Переменные окружения

```bash
DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/vuetube
REDIS_HOST=redis
REDIS_PORT=6379
CORS_ORIGINS=http://localhost:4173,http://localhost:3535
RUTUBE_CHANNEL_ID=32869212
```

## Локальный запуск

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload --port 3535
```

## Docker

```bash
docker compose up backend -d
```