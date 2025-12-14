# Оптимизированный Dockerfile для Backend

# Этап 1: Builder - установка зависимостей
FROM python:3.12-slim as builder

# Переменные окружения для сборки
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME=/opt/poetry \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Системные зависимости для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s $POETRY_HOME/bin/poetry /usr/local/bin/poetry

WORKDIR /build

# Копируем файлы зависимостей и исходный код для установки зависимостей
COPY backend/pyproject.toml backend/poetry.lock* ./
COPY backend/app ./app

# Устанавливаем зависимости
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main

# Этап 2: Runtime - финальный образ
FROM python:3.12-slim as runtime

# Runtime переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/poetry/bin:$PATH"

# Минимальные системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    chromium \
    chromium-driver \
    libnss3 \
    libxi6 \
    libgbm1 \
    fonts-liberation \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Копируем установленные пакеты из builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Копируем код приложения
COPY --chown=appuser:appuser backend/app ./app
COPY --chown=appuser:appuser backend/seed_db.py ./
COPY --chown=appuser:appuser backend/pyproject.toml ./

# Создаем директории для данных и Chrome
RUN mkdir -p /app/data /app/logs /tmp/chrome-user-data /tmp/chrome-data /tmp/chrome-cache /tmp/crashpad \
    && chown -R appuser:appuser /app /tmp/chrome-user-data /tmp/chrome-data /tmp/chrome-cache /tmp/crashpad \
    && chmod -R 777 /tmp/chrome-user-data /tmp/chrome-data /tmp/chrome-cache /tmp/crashpad

# Переключаемся на непривилегированного пользователя
USER appuser

# Переменные окружения по умолчанию
ENV DATABASE_URL="" \
    REDIS_HOST=redis \
    REDIS_PORT=6379 \
    CORS_ORIGINS="http://localhost:4173,http://localhost:3000,http://localhost:3535" \
    LOG_LEVEL=INFO \
    ENVIRONMENT=production \
    SQLITE_PATH=/app/data/db.sqlite

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3535/api/health || exit 1

# Expose порт
EXPOSE 3535

# Запуск приложения
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 3535 --workers 1 --access-log --log-level ${LOG_LEVEL}"]
