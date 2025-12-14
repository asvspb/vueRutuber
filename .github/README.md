# vueRutube

Веб-приложение для отображения видео с Rutube с автоматическим сбором данных.

## Стек технологий

| Компонент | Технология | Порт |
|-----------|------------|------|
| Frontend | Vue.js 3 + Vuetify 3 + TypeScript | 4173 |
| Backend | FastAPI (async) | 3535 |
| Database | PostgreSQL | 5432 |
| Cache | Redis | 6379 |

## Быстрый старт

```bash
# Docker (рекомендуется)
docker compose up --build -d

# Проверка
curl http://localhost:3535/api/health
open http://localhost:4173
```

## Переменные окружения

### Backend (docker-compose.yml)
```yaml
DATABASE_URL: postgresql+asyncpg://postgres:password@db:5432/vuetube
REDIS_HOST: redis
REDIS_PORT: 6379
CORS_ORIGINS: http://localhost,http://localhost:4173,http://localhost:3535
RUTUBE_CHANNEL_ID: 32869212
```

### Frontend (Dockerfile build arg)
```yaml
VITE_API_BASE_URL: http://localhost:3535/api
```

## Структура проекта

```
├── docker-compose.yml          # 4 сервиса: frontend, backend, db, redis
├── Dockerfile                  # Frontend multi-stage build
├── backend/
│   ├── Dockerfile
│   ├── app/
│   │   ├── main.py             # FastAPI app, роуты
│   │   ├── models.py           # SQLAlchemy: Movie
│   │   ├── schemas.py          # Pydantic схемы
│   │   ├── crud.py             # CRUD операции
│   │   ├── database.py         # Async PostgreSQL
│   │   └── rutube_api_scraper.py  # Rutube API скрапер
│   └── pyproject.toml
├── src/
│   ├── components/
│   │   └── MovieList.vue       # Vuetify компонент
│   ├── composables/
│   │   └── useMovies.ts
│   ├── services/
│   │   ├── api.ts              # Axios instance
│   │   └── moviesService.ts
│   └── plugins/
│       └── vuetify.ts
└── docs/
    ├── ai_developer_guide.md   # Руководство для ИИ-агентов
    └── microservices_architecture.md
```

## API Endpoints

### Movies
```
GET  /api/movies/?skip=0&limit=20
GET  /api/movies/{id}
GET  /api/movies/year/{year}
GET  /api/movies/genre/{genre}
POST /api/movies/
PUT  /api/movies/{id}
DELETE /api/movies/{id}
```

### Scraper
```
POST /api/scrape/rutube?limit=100
```

### Health
```
GET /api/health
```

## Скрипты

```bash
# Dev
npm run dev           # Frontend dev server (5173)
npm run build         # Production build
npm run preview       # Preview build (4173)

# Тесты
npm run test          # Unit tests (Vitest)
npm run e2e           # E2E tests (Playwright)

# Линтинг
npm run lint          # ESLint + Stylelint
```

## Локальный запуск (без Docker)

```bash
# Backend
cd backend
poetry install
poetry run uvicorn app.main:app --reload --port 3535

# Frontend
npm install
npm run dev
```

## Документация

- `docs/ai_developer_guide.md` — руководство для ИИ-агентов
- `docs/microservices_architecture.md` — архитектура системы
- `docs/documentation_rules.md` — правила документирования