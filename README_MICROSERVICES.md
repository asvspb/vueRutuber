# vueRutube — Архитектура

## Обзор

Веб-приложение для отображения видео с Rutube с автоматическим сбором данных.

### Компоненты

| Сервис | Технология | Порт |
|--------|------------|------|
| Frontend | Vue.js 3 + Vuetify 3 | 4173 |
| Backend | FastAPI (async) | 3535 |
| Database | PostgreSQL | 5432 |
| Cache | Redis | 6379 |

## Структура проекта

```
backend/
├── app/
│   ├── main.py               # FastAPI app, роуты, background tasks
│   ├── models.py             # SQLAlchemy: Movie
│   ├── schemas.py            # Pydantic схемы
│   ├── crud.py               # CRUD операции
│   ├── database.py           # Async PostgreSQL (asyncpg)
│   └── rutube_api_scraper.py # Rutube API скрапер (aiohttp)
├── pyproject.toml
└── requirements.txt
```

```
src/
├── components/
│   └── MovieList.vue         # Vuetify компонент (v-card, v-chip)
├── composables/
│   └── useMovies.ts          # Композабл для работы с фильмами
├── services/
│   ├── api.ts                # Axios instance
│   └── moviesService.ts      # API методы
└── plugins/
    └── vuetify.ts            # Vuetify конфигурация
```

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

## API Endpoints

### Movies
```
GET  /api/movies/?skip=0&limit=20  # Список с пагинацией
GET  /api/movies/{id}              # По ID
GET  /api/movies/year/{year}       # По году
GET  /api/movies/genre/{genre}     # По жанру
POST /api/movies/                  # Создать
PUT  /api/movies/{id}              # Обновить
DELETE /api/movies/{id}            # Удалить
```

### Scraper
```
POST /api/scrape/rutube?limit=100  # Запуск скрапера
```

### Health
```
GET /api/health                    # Статус сервисов
```

## Запуск

### Docker (рекомендуется)

```bash
docker compose up --build -d
```

### Локально

```bash
# Backend
cd backend
poetry install
poetry run uvicorn app.main:app --reload --port 3535

# Frontend
npm install
npm run dev
```

## Rutube Scraper

Автоматический сбор данных с Rutube API:

```python
# API endpoint
https://rutube.ru/api/video/person/{CHANNEL_ID}/?page=1&page_size=20

# Расписание: раз в 24 часа (asyncio background task)
```

Ручной запуск:
```bash
curl -X POST "http://localhost:3535/api/scrape/rutube?limit=100"
```

## Переменные окружения

```yaml
# Backend
DATABASE_URL: postgresql+asyncpg://postgres:password@db:5432/vuetube
REDIS_HOST: redis
REDIS_PORT: 6379
CORS_ORIGINS: http://localhost,http://localhost:4173,http://localhost:3535
RUTUBE_CHANNEL_ID: 32869212

# Frontend (build-time)
VITE_API_BASE_URL: http://localhost:3535/api
```

## Frontend компоненты

### MovieList.vue (Vuetify 3)
- `v-container`, `v-row`, `v-col` — сетка
- `v-card`, `v-img` — карточки фильмов
- `v-chip` — метки (год, жанр, просмотры)
- `v-btn` — кнопки пагинации
- `v-progress-circular` — индикатор загрузки

### useMovies.ts
```typescript
const { movies, loading, error, fetchMovies } = useMovies()
```