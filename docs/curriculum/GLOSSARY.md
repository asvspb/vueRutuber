# Глоссарий курса (очень подробный)

Назначение: единый справочник терминов и понятий, встречающихся в учебном проекте и материалах. Структурирован по областям: общие веб‑понятия, фронтенд, бэкенд, базы данных, кэш/брокеры, тестирование, инфраструктура (CI/CD), безопасность и процессы разработки.

Формат: краткое определение + контекст использования в курсе + при необходимости — отсылки на документы в `docs/curriculum`.

---

## 1) Общие веб‑понятия и протоколы
- HTTP (HyperText Transfer Protocol): протокол передачи данных в вебе. Методы: GET/POST/PUT/PATCH/DELETE. Статусы: 2xx — успех, 4xx — ошибки клиента, 5xx — ошибки сервера.
- HTTPS: HTTP поверх TLS/SSL для шифрования трафика. Требуется для безопасности и доверия.
- REST: архитектурный стиль для API; ресурсы, единые интерфейсы, без состояния. В курсе — эндпоинты FastAPI.
- JSON: текстовый формат обмена данными (объекты/массивы, строки/числа/логические/Null). Основной формат ответов/запросов API.
- CORS (Cross‑Origin Resource Sharing): механизм браузера, ограничивающий запросы с других источников. В курсе настраивается в FastAPI через CORS middleware.
- URL/URI: унифицированные локаторы ресурсов. Важен для конфигурации API (VITE_API_BASE_URL, PW_BASE_URL).
- Cookie/Session/Token: способы поддержания состояния и идентификации пользователя. В проде — прорабатываются вместе с безопасностью.

## 2) Frontend (Vue, Vite, стили)
- Vue 3: прогрессивный фреймворк для интерфейсов. В курсе — только Composition API и `<script setup>`.
- Composition API: декларативная модель через `ref`, `reactive`, `computed`, `watch`, хуки жизненного цикла.
- `<script setup>`: синтаксический сахар для SFC — лаконичный код без `export default`.
- SFC (Single File Component): единый файл с `<template>`, `<script>`, `<style>`.
- Props/Emits: входные параметры и события компонента.
- Vite: сборщик и dev‑сервер. Порты dev: 5173; preview: 4173. Переменные среды — `import.meta.env`.
- Env переменные фронта: префикс `VITE_` (например, `VITE_API_BASE_URL`) — доступны в клиентском коде.
- SCSS (Sass): надстройка над CSS с переменными, миксинами, вложенностью. В проекте — каталог `src/styles`.
- BEM (Block–Element–Modifier): методология нейминга классов (`block__element--modifier`) для читаемых и масштабируемых стилей. См. [bem.md](./bem.md).
  - Утилиты и состояния: префиксы `u-*` (утилитарные классы, проектный уровень) и `is-*` (состояния), разрешены линтером.
  - Stylelint: линтер CSS/SCSS. Правило `selector-class-pattern` — проверка соответствия BEM/разрешённым префиксам для SFC (`postcss-html`).
  - Flexbox: одномерная раскладка. Ключевые свойства: `display:flex`, `justify-content`, `align-items`, `flex-wrap`, `flex-grow/shrink`.
  - CSS Grid: двумерная раскладка. Ключевые свойства: `display:grid`, `grid-template-columns/rows`, `gap`, `minmax`, `auto-fit/auto-fill`, `align-items`.
- CSS‑модули/Scoped styles: механизмы изоляции стилей в SFC. В курсе акцент на `scoped` + BEM.
- SPA: приложение, работающее в одном документе, обновляет UI без полной перезагрузки.
- SSR/SSG: серверный/статический рендеринг. Отдельный модуль — Nuxt (опционально).

## 3) Backend (FastAPI, Pydantic, SQLAlchemy)
- FastAPI: фреймворк для быстрых API на Python. Аннотации типов → валидация и OpenAPI.
- Pydantic (v2): библиотека валидации и сериализации данных. В курсе — модели схем ввода/вывода (`schemas.py`).
- Dependency Injection (DI): внедрение зависимостей через параметры функций/эндпоинтов. В FastAPI — `Depends`.
- APIRouter: механизм модульного роутинга в FastAPI (`from fastapi import APIRouter`), позволяет разделять эндпоинты по модулям и подключать их в `main`. Целевой рефакторинг.
- Middleware: прослойки обработки запросов/ответов, например, CORS.
- Uvicorn: ASGI‑сервер для запуска FastAPI.
- Lifespan/startup/shutdown: механизм инициализации/освобождения ресурсов при старте/остановке приложения.
- httpx: HTTP‑клиент для тестов и утилит. В курсе — `httpx.AsyncClient` для интеграционных тестов FastAPI.
- Redis (клиент): `redis.asyncio` — асинхронный клиент Redis; используется для `/counter`, health‑check.
- python‑dotenv: загрузка переменных окружения из `.env` (приоритет OS env > .env > дефолты в коде).

## 4) SQLAlchemy 2.0 Async и ORM
- SQLAlchemy: ORM/ядро SQL для Python. Версия 2.0 — улучшенные API и типичный async‑стек.
- Async Engine: `create_async_engine()` — объект работы с БД, управляет подключениями и транзакциями.
- AsyncSession: единица работы с ORM (операции CRUD, транзакции). Создаётся через `async_sessionmaker`.
- Транзакция: атомарная последовательность операций; в SQLAlchemy — `session.begin()`/контекст менеджер.
- Миграции: управление версией схемы БД; в курсе — Alembic.
- Ревизия Alembic: файл‑описание изменения схемы (upgrade/downgrade). См. [alembic_cookbook.md](./alembic_cookbook.md).
- asyncpg: драйвер PostgreSQL для async‑стека.
- aiosqlite: драйвер SQLite для async‑стека.
- Eager/Lazy loading: стратегии загрузки связанных данных (`selectinload`, `joinedload`).
- Expire on commit: флаг инвалидации полей ORM после коммита; по умолчанию True, часто отключают.

## 5) Базы данных
- SQLite: встраиваемая реляционная БД. Учебная БД по умолчанию (файл). Драйвер — `aiosqlite`.
- PostgreSQL: промышленная реляционная БД. В прод‑этапе — `asyncpg` драйвер + Alembic миграции.
- Connection URL: строка подключения к БД. Приоритет `DATABASE_URL` > `SQLITE_PATH` в учебном проекте.
- Индексы/Ограничения: механизмы оптимизации запросов и обеспечения целостности.
- JSONB: бинарный JSON‑тип в Postgres для полуструктурированных данных (индексируется GIN).
- GIN индекс: ускоряет поиск по JSONB/массивам.
- MVCC: мультиверсионность для конкурентного доступа (неблокирующие SELECT).
- FOR UPDATE: блокировка строк в транзакции для честных операций (покупка последней единицы товара).
- EXPLAIN ANALYZE: план выполнения и реальные показатели, помогает оптимизировать.

## 6) Redis (кэш/брокер)
- Redis: хранилище ключ‑значение в памяти. Типы: строки, списки, множества, хэши, ZSET.
- Пайплайн: группировка команд для уменьшения накладных расходов (может быть транзакционным/нетранзакционным).
- Транзакция (MULTI/EXEC): атомарное выполнение последовательности команд.
- TTL/EXPIRE: время жизни ключа.
- Pub/Sub: механизм публикации/подписки (в курсе упоминается кратко).
- Lua scripts: атомарная логика на стороне Redis (rate limiting, обновление рейтингов).
- Cache‑Aside: паттерн кэширования (сначала кэш, иначе БД → записать в кэш).

## 7) Тестирование
- Unit‑тесты: тесты маленьких единиц логики (функции/компоненты). Фронт — Vitest.
- Интеграционные тесты: тесты связей между модулями/слоями. Бэк — Pytest + httpx.AsyncClient.
  - In‑process клиент: `AsyncClient(app=app, base_url="http://test")` — быстрые тесты без сети.
  - anyio/pytest‑asyncio: маркировки для async тестов (`@pytest.mark.anyio`).
- E2E тесты (End‑to‑End): проверяют сценарии пользователя в браузере. В курсе — Playwright.
- Pytest: фреймворк тестов. Плагины: `pytest‑asyncio`, `pytest‑cov` (покрытие).
- Фикстуры: механизмы подготовки/освобождения ресурсов для тестов (session/module/function scope).
- Testcontainers: запуск реальных сервисов (Postgres/Redis) в контейнерах на время тестов. См. [testcontainers_advanced.md](./testcontainers_advanced.md).
- Coverage (покрытие): доля кода, исполненного тестами. Пороги покрытия задаются в CI и vitest.config.js.
- Vitest: тестовый раннер для Vue/TS проектов (аналог Jest). Поддерживает покрытие (`@vitest/coverage-v8`).
- Playwright: e2e‑раннер, управляет браузерами. Базовый URL задается через `PW_BASE_URL`. 

## 8) Инфраструктура, Docker, CI/CD
- Docker: контейнеризация приложений. Dockerfile — рецепт образа.
- Docker Compose: оркестрация многоконтейнерных приложений локально.
- Healthcheck: проверка готовности сервиса (например, `/health`). Описывается в Compose и Dockerfile.
  - service_healthy: условие зависимости `depends_on: condition: service_healthy` в Compose.
- Volume: том для устойчивого хранения данных БД.
- Network: виртуальная сеть между сервисами в Compose.
- Entrypoint/CMD: команды запуска контейнера.
- GitHub Actions: менеджер CI/CD‑конвейеров. Конфигурация — YAML‑workflow в `.github/workflows`.
- Workflow: файл описания пайплайна (триггеры, jobs, permissions).
- Job: логический этап (выполняется на отдельном раннере/ВМ).
- Step: отдельное действие в job (checkout, setup, run tests и т. п.).
- Artifact: артефакт сборки/покрытия/логов, загружаемый из CI.
- Cache: кэш зависимостей (npm/pip) для ускорения сборки.
- Matrix build: прогон сборки по матрице версий (Node 18/20 и т. д.).
- ESLint/Stylelint: линтеры кода/стилей. Fail‑on‑error в CI — пайплайн падает при ошибках.
- Ruff/Flake8: линтеры Python кода.
- wait-on: утилита ожидания готовности сервиса (используется для preview на 4173 перед e2e).
- Coverage thresholds: пороги покрытия (vitest.config.js, `--cov-fail-under`).

## 9) Переменные окружения и конфигурация
- Переменные окружения (env vars): конфигурация через OS‑переменные. На фронте доступны только с префиксом `VITE_`.
- `.env`/`python‑dotenv`: файл локальной конфигурации и библиотека загрузки.
- `VITE_API_BASE_URL`: базовый URL API для фронта. Влияет на `fetch`/`axios`/`$fetch`.
- `PW_BASE_URL`: базовый URL для Playwright.
- `DATABASE_URL`/`SQLITE_PATH`: параметры БД в бэкенде (приоритет `DATABASE_URL`).
- `REDIS_HOST`/`REDIS_PORT`: параметры Redis.

## 10) Безопасность
- CORS: политика кросс‑доменных запросов. В курсе — whitelist `http://localhost:5173` и `http://localhost:4173` (и `:3000` при Nuxt).
- CSP (Content Security Policy): политика безопасности контента. В прод — ограничение источников скриптов/ресурсов.
- HSTS: заголовок, заставляющий использовать только HTTPS.
- HttpOnly/SameSite Cookie: защита от XSS/CSRF для refresh‑токенов.
- JWT: access (короткий, в памяти), refresh (длинный, в HttpOnly), ротация.
- CSRF Token: защита POST из чужих источников.
- Валидация: проверка входных данных (Pydantic). Защита от XSS/SQL injection — на уровне валидации/ORM/шаблонов.
- Rate limit: ограничение частоты, можно реализовать на Redis (продвинутый модуль).

## 11) Процессы разработки
- Git workflow: ветки, PR, code review.
- Docs‑Driven: документация задает ожидаемое поведение (наш учебник).
- CI/CD: пайплайн, который собирает, тестирует, прогоняет миграции (см. [cicd.md](./cicd.md)).
- Confluence/Jira: системы документации и трекинга задач (на выбор команды; опционально).

## 12) Nuxt (опционально)
- Nuxt: метафреймворк для Vue с SSR/SSG/Hybrid режимами.
- Структура: `pages/`, `layouts/`, `components/`, `composables/`, `server/api/`, `plugins/`.
- `NUXT_PUBLIC_*`/`NUXT_*`: публичные/приватные env переменные.
- `$fetch`/`useFetch`: универсальные способы запросов с учётом SSR.

## 13) Полезные понятия и приёмы
- Dev/Preview режимы (Vite): разные порты, разная статика/оптимизация.
- Base URL (Playwright): конфиг по умолчанию и переключение через `PW_BASE_URL`.
- Кэширование: хранение часто используемых данных в памяти/Redis.
- Идempotентность: свойство операции не менять результат при повторе (важно для некоторых API).
- Консистентность/целостность: свойства данных, поддерживаемые ограничениями и транзакциями.

---

Ссылки на учебные материалы
- Frontend: [vue.md](./vue.md), [vite.md](./vite.md), [css.md](./css.md), [bem.md](./bem.md)
- Backend: [fastapi.md](./fastapi.md), [sqlite.md](./sqlite.md), [sqlalchemy_async.md](./sqlalchemy_async.md), [redis.md](./redis.md)
- Тестирование: [tests.md](./tests.md), [httpx_essentials.md](./httpx_essentials.md), [testcontainers_advanced.md](./testcontainers_advanced.md)
- Инфраструктура и CI/CD: [docker.md](./docker.md), [docker_healthcheck.md](./docker_healthcheck.md), [cicd.md](./cicd.md)
- Миграции и БД: [postgres.md](./postgres.md), [alembic_cookbook.md](./alembic_cookbook.md)
- Конфигурация и безопасность: [python-dotenv.md](./python-dotenv.md), [security.md](./security.md)
- Дополнительно: (nuxt.md — при добавлении)
