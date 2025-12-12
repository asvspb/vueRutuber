# Vue.js + FastAPI Learning Project

Этот проект представляет собой полнофункциональное веб-приложение, состоящее из фронтенда на Vue.js с TypeScript и бэкенда на FastAPI с Python.

## Архитектура

- **Frontend**: Vue 3 + TypeScript + Vite + Pinia + Vue Router
- **Backend**: FastAPI + SQLAlchemy + Pydantic
- **Database**: SQLite (по умолчанию) / PostgreSQL
- **Testing**: Vitest (unit), Playwright (e2e), Pytest (backend)
- **Containerization**: Docker + Docker Compose

## Структура проекта

- `src/` - Клиентская часть на Vue.js с TypeScript
- `backend/` - Серверная часть на FastAPI
- `docs/` - Документация и макеты
- `e2e/` - Сквозные тесты
- `docker-compose.yml` - Конфигурация для запуска с Docker

## Быстрый старт

1. Установите зависимости:
   ```bash
   npm install
   cd backend && poetry install
   ```

2. Запустите с Docker Compose:
   ```bash
   docker-compose up
   ```

3. Или запустите локально:
   ```bash
   # Frontend
   npm run dev

   # Backend
   cd backend && poetry run uvicorn app.main:app --reload
   ```

## Скрипты

- `npm run dev` - Запуск dev сервера
- `npm run build` - Сборка для продакшена
- `npm run type-check` - Проверка типов TypeScript
- `npm run test` - Запуск unit тестов
- `npm run e2e` - Запуск e2e тестов

## Особенности

- Полная типизация с TypeScript
- Современный стек технологий
- Docker поддержка
- Автоматизированное тестирование
- ESLint и Prettier для качества кода