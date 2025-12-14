# vueRutube

Веб-приложение для отображения фильмов с Rutube. Автоматический сбор данных через Rutube API.

## 🏗️ Архитектура

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
              │  :5432   │ │  :6379   │ │ (volume) │
              └──────────┘ └──────────┘ └──────────┘
```

## 🚀 Быстрый старт

### Требования
- Docker и Docker Compose v2

### Запуск

```bash
# Клонировать репозиторий
git clone https://github.com/asvspb/vueRutuber.git
cd vueRutuber

# Создать директорию для логов
mkdir -p logs/backend

# Запустить все сервисы
docker compose up --build -d

# Проверить статус
docker compose ps
```

### Доступ

| Сервис | URL |
|--------|-----|
| Frontend | http://localhost:4173 |
| Backend API | http://localhost:3535/api |
| API Docs | http://localhost:3535/docs |
| Health Check | http://localhost:3535/api/health |

## 📋 API Endpoints

### Movies API
```bash
# Получить фильмы (с пагинацией)
curl "http://localhost:3535/api/movies/?skip=0&limit=20"

# Получить фильм по ID
curl http://localhost:3535/api/movies/1

# Фильмы по году
curl http://localhost:3535/api/movies/year/2023

# Фильмы по жанру
curl http://localhost:3535/api/movies/genre/драма
```

### Scraper API
```bash
# Запустить скрапер вручную (получить 100 фильмов)
curl -X POST "http://localhost:3535/api/scrape/rutube?limit=100"
```

## 🎬 Rutube Scraper

Скрапер автоматически собирает данные с Rutube API:
- Запускается **раз в сутки** (background task)
- Получает: название, год, thumbnail, просмотры, длительность, жанр, описание
- Сохраняет в PostgreSQL

```python
# Ручной запуск скрапера
POST /api/scrape/rutube?limit=100
```

## 🔧 Конфигурация

### Переменные окружения (docker-compose.yml)

```yaml
# Database
DATABASE_URL: postgresql+asyncpg://postgres:password@db:5432/vuetube

# Redis
REDIS_HOST: redis
REDIS_PORT: 6379

# CORS
CORS_ORIGINS: http://localhost,http://localhost:4173,http://localhost:3535

# Rutube
RUTUBE_CHANNEL_ID: 32869212  # ID канала для скрапинга
```

## 📁 Структура проекта

```
├── docker-compose.yml          # Конфигурация сервисов
├── docker-compose.override.yml # Dev overrides
├── Dockerfile                  # Frontend build
├── backend/
│   ├── Dockerfile
│   ├── app/
│   │   ├── main.py             # FastAPI приложение
│   │   ├── models.py           # SQLAlchemy модели
│   │   ├── schemas.py          # Pydantic схемы
│   │   ├── crud.py             # CRUD операции
│   │   ├── database.py         # Конфигурация БД
│   │   └── rutube_api_scraper.py  # Rutube API скрапер
│   ├── pyproject.toml
│   └── requirements.txt
├── src/
│   ├── components/
│   │   └── MovieList.vue       # Vuetify компонент списка фильмов
│   ├── composables/
│   │   └── useMovies.ts        # Composable для работы с фильмами
│   ├── services/
│   │   ├── api.ts              # Axios instance
│   │   └── moviesService.ts    # API сервис фильмов
│   └── plugins/
│       └── vuetify.ts          # Vuetify конфигурация
└── docs/                       # Документация
```

## 🛠️ Технологии

### Frontend
- Vue.js 3 + TypeScript
- Vuetify 3 (Material Design)
- Pinia (state management)
- Vue Router 4
- Vite

### Backend
- FastAPI
- SQLAlchemy (async)
- Pydantic
- aiohttp (для Rutube API)
- PostgreSQL
- Redis

### Infrastructure
- Docker & Docker Compose
- Multi-stage builds

## 🔍 Отладка

```bash
# Логи всех сервисов
docker compose logs -f

# Логи конкретного сервиса
docker compose logs -f backend

# Статус контейнеров
docker compose ps

# Перезапуск
docker compose restart backend
```

## 📄 License

MIT License