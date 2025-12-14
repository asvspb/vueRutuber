# Инструкция для ИИ-агента: vueRutube

## Архитектура проекта

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
```

## Стек технологий

### Frontend
- Vue.js 3 + TypeScript
- Vuetify 3 (Material Design компоненты)
- Pinia (state management)
- Vue Router 4
- Vite (сборка)
- SCSS

### Backend
- FastAPI (async)
- SQLAlchemy (async с asyncpg)
- Pydantic v2
- aiohttp (HTTP клиент для Rutube API)
- PostgreSQL
- Redis

## Структура проекта

```
├── docker-compose.yml          # 4 сервиса: frontend, backend, db, redis
├── docker-compose.override.yml # Dev overrides
├── Dockerfile                  # Frontend multi-stage build
├── backend/
│   ├── Dockerfile
│   ├── app/
│   │   ├── main.py             # FastAPI app, роуты, background tasks
│   │   ├── models.py           # SQLAlchemy: Movie
│   │   ├── schemas.py          # Pydantic схемы
│   │   ├── crud.py             # CRUD операции
│   │   ├── database.py         # Async PostgreSQL
│   │   └── rutube_api_scraper.py  # Rutube API скрапер
│   ├── pyproject.toml
│   └── requirements.txt
├── src/
│   ├── components/
│   │   └── MovieList.vue       # Главный компонент (Vuetify)
│   ├── composables/
│   │   └── useMovies.ts
│   ├── services/
│   │   ├── api.ts              # Axios instance
│   │   └── moviesService.ts
│   └── plugins/
│       └── vuetify.ts
└── docs/
```

## Ключевые файлы

| Файл | Назначение |
|------|------------|
| `docker-compose.yml` | Конфигурация всех сервисов |
| `Dockerfile` | Frontend: build + serve |
| `backend/Dockerfile` | Backend: Python + FastAPI |
| `backend/app/main.py` | API endpoints, scraper scheduler |
| `backend/app/rutube_api_scraper.py` | Сбор данных с Rutube API |
| `src/components/MovieList.vue` | Vuetify компонент списка фильмов |
| `src/services/api.ts` | Axios с `VITE_API_BASE_URL` |

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

## Rutube Scraper

Автоматический сбор данных с Rutube API:
- **Endpoint**: `https://rutube.ru/api/video/person/{CHANNEL_ID}/`
- **Интервал**: раз в 24 часа (asyncio background task)
- **Данные**: title, thumbnail, views, duration, genre, description

## Переменные окружения

```yaml
# Backend (docker-compose.yml)
DATABASE_URL: postgresql+asyncpg://postgres:password@db:5432/vuetube
REDIS_HOST: redis
REDIS_PORT: 6379
CORS_ORIGINS: http://localhost,http://localhost:4173,http://localhost:3535
RUTUBE_CHANNEL_ID: 32869212

# Frontend (Dockerfile build arg)
VITE_API_BASE_URL: http://localhost:3535/api
```

## Команды

```bash
# Запуск
docker compose up --build -d

# Логи
docker compose logs -f backend

# Перезапуск
docker compose restart backend

# Остановка
docker compose down
```

## Правила для ИИ-агента

1. **Перед изменениями** — изучить связанные файлы через codebase-retrieval
2. **Frontend** — использовать Vuetify компоненты (v-card, v-chip, v-btn, etc.)
3. **Backend** — async/await, Pydantic v2, SQLAlchemy async
4. **Docker** — проверять сборку после изменений
5. **Зависимости** — использовать package managers (npm, poetry)
6. **Документация** — обновлять при изменении API или архитектуры

## Отладка

```bash
# Проверка API
curl http://localhost:3535/api/health
curl http://localhost:3535/api/movies/?limit=3

# Логи контейнера
docker compose logs backend --tail=50

# Проверка переменных
docker compose exec frontend env | grep VITE
```