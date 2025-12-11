FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME=/opt/poetry

# Системные пакеты (при необходимости для сборки зависимостей)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s $POETRY_HOME/bin/poetry /usr/local/bin/poetry

WORKDIR /app

# Копируем только файлы декларации зависимостей для кеша
COPY pyproject.toml poetry.lock* ./

# В контейнере удобно ставить в системное окружение (без виртуального env)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main

# Затем копируем остальной код
COPY .env .env
COPY app ./app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

