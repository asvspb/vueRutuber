# vuExpert

Проект vuExpert - это заготовка для современного веб-приложения, разработанное с использованием фреймворка Vue.js. Проект включает в себя примеры работы с базами данных (SQLite, Redis), компоненты для документации и стилизацию с использованием SCSS.

## Переменные окружения

- Для фронтенда используем `VITE_API_BASE_URL` (см. docs/environment_variables.md)
- Для e2e тестов можно указать `PW_BASE_URL` (5173 для dev, 4173 для docker preview)

Для конфигурации приложения используйте .env файлы:

- `backend/.env` - конфигурация для бэкенда
- `.env` - конфигурация для фронтенда

Смотрите `docs/environment_variables.md` для подробной информации о доступных переменных.

## Структура проекта

- `.gitignore` - файл настроек игнорирования файлов для Git
- `index.html` - основной HTML-файл приложения
- `package.json` - файл зависимостей и настроек проекта
- `package-lock.json` - файл блокировки версий зависимостей
- `vite.config.js` - конфигурационный файл Vite
- `eslint.config.js` - конфигурация ESLint
- `playwright.config.js` - конфигурация для E2E тестов
- `Dockerfile` - конфигурация для контейнера фронтенда
- `.stylelintrc.cjs` - конфигурация Stylelint
- `.qodo/` - директория для служебных файлов
- `src/` - исходный код приложения
  - `App.vue` - главный компонент приложения
  - `main.js` - точка входа в приложение
  - `README.md` - описание директории src
 - `components/` - компоненты Vue
    - `README.md` - описание компонентов
    - `DatabaseConnectionExample.vue` - примеры подключения к базам данных
    - `DatabaseExample.vue` - примеры работы с базами данных
    - `Documentation.vue` - документация по технологиям
    - `HelloWorld.vue` - пример компонента
    - `__tests__/` - unit тесты
  - `composables/` - композаблы Vue
 - `services/` - сервисы приложения
  - `styles/` - файлы стилей
    - `README.md` - описание стилевых файлов
    - `main.scss` - основной файл стилей
    - `mixins.scss` - миксины SCSS
    - `variables.scss` - переменные SCSS
- `backend/` - бэкенд на FastAPI
  - `Dockerfile` - конфигурация контейнера бэкенда
  - `pyproject.toml` - конфигурация зависимостей Poetry
  - `poetry.lock` - файл блокировки версий зависимостей
 - `app/` - основное приложение
    - `main.py` - точка входа FastAPI
    - `database.py` - конфигурация базы данных
    - `models.py` - модели SQLAlchemy
    - `schemas.py` - схемы Pydantic
    - `crud.py` - операции CRUD
  - `tests/` - тесты бэкенда
- `docs/` - документация
  - `ai_developer_guide.md` - руководство по работе с ИИ-разработчиком
  - `documentation_rules.md` - правила документирования
  - `environment_variables.md` - переменные окружения
  - `poetry_migration_plan.md` - план миграции на Poetry
 - `project_architecture_and_philosophy.md` - архитектура и философия проекта
  - `qwen_coder_integration.md` - интеграция с Qwen Coder
  - `curriculum/` - учебные материалы
    - `bem.md` - методология БЭМ
    - `cicd.md` - непрерывная интеграция и доставка
    - `css.md` - стилизация
    - `docker.md` - контейнеризация
    - `docker_healthcheck.md` - проверки состояния в Docker
    - `fastapi.md` - фреймворк FastAPI
    - `GLOSSARY.md` - глоссарий
    - `MASTER_PROMPT.md` - основной промпт
    - `META-PROMT.md` - мета-промпт
    - `MODULE_ASSESSMENT.md` - оценка модулей
    - `py.md` - Python
    - `python-dotenv.md` - переменные окружения
    - `redis.md` - Redis
    - `sqlite.md` - SQLite
    - `ts.md` - TypeScript
    - `vite.md` - сборщик Vite
    - `vue.md` - фреймворк Vue.js
  - `wireframes/` - макеты интерфейсов
- `e2e/` - end-to-end тесты
- `.github/` - конфигурации GitHub

## Запуск проекта

### Локальный запуск

1. Установите зависимости: `npm ci`
2. Установите зависимости бэкенда: `cd backend && poetry install`
3. Запустите бэкенд: `cd backend && poetry run uvicorn app.main:app --reload`
4. В новом терминале запустите фронтенд: `npm run dev` (по умолчанию порт 5173)

### Запуск с Docker

1. Убедитесь, что у вас установлен Docker и Docker Compose
2. Запустите все сервисы: `docker-compose up --build`
3. Приложение будет доступно по адресу `http://localhost:4173`

### Скрипты

- Dev-сервер: `npm run dev` (по умолчанию порт 5173)
- Сборка: `npm run build`
- Preview (локально): `npm run preview` (порт 4173)
- Линтинг кода и стилей: `npm run lint`
- Только стили: `npm run lint:css`, автоисправление: `npm run lint:css:fix`
- Unit-тесты: `npm run test` / покрытие: `npm run test:coverage`
- E2E: `npm run e2e` (PW_BASE_URL берётся из окружения)

## Стек, линтеры и учебные материалы

Учебные материалы построены в формате уроков с двумя уровнями: Basic (минимум для MVP) и Advanced (архитектура/безопасность/производительность). См. раздел docs/curriculum.

### Стек и линтеры
- Frontend: Vue 3 (Composition API + `<script setup>`), Vite, SCSS
- Backend: FastAPI, SQLAlchemy Async, SQLite/Redis (старт), PostgreSQL (прод)
- Линтеры:
  - ESLint (flat config `eslint.config.js`) + плагины: `eslint-plugin-vue`, `eslint-plugin-vuejs-accessibility`
  - Stylelint (`.stylelintrc.cjs`) с правилами BEM + поддержкой Vue SFC
- Конвенции стилей: BEM (`block__element--modifier`), допускаются `u-*` (утилиты) и `is-*` (состояния)

### Тестирование
- Unit-тесты: Vitest с DOM Testing Library
- E2E тесты: Playwright
- Покрытие кода: Istanbul через Vitest

## Прокси и порты

- Dev: фронт 5173, бэкенд 8000; preview: 4173
- В dev рекомендуем proxy `/api` и `/ws` в `vite.config.js`

## Зависимости

Проект использует Vue.js, Vite, FastAPI, SQLAlchemy, Redis и другие библиотеки, перечисленные в package.json и pyproject.toml.

## Архитектура

Проект состоит из двух основных частей:

### Фронтенд (Vue.js)
- Главный компонент `App.vue` включает в себя примеры использования технологий
- Компоненты документации для изучения Vue, SCSS, SQLite и Redis
- Система стилей на основе SCSS с использованием переменных и миксинов
- Поддержка BEM-методологии для структурирования CSS

### Бэкенд (FastAPI)
- REST API с эндпоинтами для работы с базами данных
- Поддержка SQLite и Redis
- Модели данных с использованием SQLAlchemy
- Схемы валидации Pydantic
- Поддержка CORS для взаимодействия с фронтендом

### Базы данных
- SQLite: реляционная база данных для хранения основных данных
- Redis: in-memory хранилище для кэширования и сессий
- Поддержка асинхронных операций с использованием SQLAlchemy

## Документация

Документация проекта включает в себя учебные материалы по всем используемым технологиям:
- Vue.js: компоненты, реактивность, жизненный цикл
- SCSS: переменные, миксины, вложенность
- SQLite: SQL-запросы, таблицы, индексы
- Redis: ключ-значение операции, структуры данных