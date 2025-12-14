# Архитектура vueRutube

## Текущая реализация

```
┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Backend       │
│   Vue.js 3      │     │   FastAPI       │
│   Vuetify 3     │     │   Port: 3535    │
│   Port: 4173    │     └────────┬────────┘
└─────────────────┘              │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │PostgreSQL│ │  Redis   │ │  Logs    │
              └──────────┘ └──────────┘ └──────────┘
                    ▲
                    │
              ┌──────────┐
              │ Rutube   │
              │   API    │
              └──────────┘
```

## Компоненты

### Frontend (Vue.js 3 + Vuetify 3)
- **Порт**: 4173
- **Технологии**: Vue 3, TypeScript, Vuetify 3, Pinia, Vue Router 4, Vite
- **Компоненты**: MovieList.vue (v-card, v-chip, v-btn)
- **API клиент**: Axios с `VITE_API_BASE_URL`

### Backend (FastAPI)
- **Порт**: 3535
- **Технологии**: FastAPI, SQLAlchemy (async), Pydantic v2, aiohttp
- **Модель**: Movie (title, year, thumbnail_url, views, duration, genre, description)
- **Скрапер**: `rutube_api_scraper.py` — сбор данных с Rutube API

### PostgreSQL
- **Порт**: 5432
- **Драйвер**: asyncpg
- **Таблица**: movies

### Redis
- **Порт**: 6379
- **Использование**: кэширование, счётчики

## Модель данных Movie

```python
class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    year = Column(Integer)
    thumbnail_url = Column(String)
    views = Column(Integer, default=0)
    added_at = Column(DateTime, default=func.now())
    source_url = Column(String)
    duration = Column(String)           # формат "HH:MM:SS"
    description = Column(Text)
    genre = Column(String)
    is_active = Column(Boolean, default=True)
```

## Rutube API Scraper

Автоматический сбор данных с официального Rutube API:

```python
# API endpoint
https://rutube.ru/api/video/person/{CHANNEL_ID}/?page=1&page_size=20

# Получаемые данные
- title, description
- thumbnail_url
- hits (просмотры)
- duration (секунды → HH:MM:SS)
- category.name (жанр)
- created_ts (дата → год)
```

**Расписание**: раз в 24 часа (asyncio background task в `main.py`)

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
POST /api/scrape/rutube?limit=100  # Запуск скрапера вручную
```

### Health
```
GET /api/health                    # Статус сервисов
```

## Docker Compose

```yaml
services:
  frontend:
    build: .
    ports: ["4173:4173"]

  backend:
    build: ./backend
    ports: ["3535:3535"]
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:password@db:5432/vuetube
      REDIS_HOST: redis

  db:
    image: postgres:15-alpine
    ports: ["5432:5432"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
```

## Масштабирование

Текущая архитектура поддерживает:
- Горизонтальное масштабирование backend (несколько реплик)
- Отдельное масштабирование PostgreSQL и Redis
- Добавление новых источников данных (других каналов Rutube)