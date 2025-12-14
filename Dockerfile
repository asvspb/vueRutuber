# Многоэтапная сборка Vite+Vue SPA

# Этап 1: сборка фронтенда
FROM node:18-alpine AS builder

WORKDIR /app

# Установим зависимости
COPY package*.json ./
RUN npm ci

# Копируем исходники
COPY . .

# Устанавливаем переменную окружения для API (вкомпилируется в билд)
ARG VITE_API_BASE_URL=http://localhost:3535/api
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Собираем приложение
RUN npm run build

# Этап 2: легкий образ для отдачи статики через serve
FROM node:18-alpine AS runner

WORKDIR /app

# Копируем только прод-артефакты и файлы, нужные для запуска
COPY package*.json ./
COPY --from=builder /app/dist ./dist

# Копируем также исходники для dev режима
COPY . .

# Устанавливаем ВСЕ зависимости (включая dev) для поддержки vite dev server
RUN npm ci

# Порт для доступа к приложению
ENV PORT=4173
EXPOSE 4173

# Команда запуска: отдача статики через serve (может быть переопределена в docker-compose)
CMD ["npx", "serve", "-s", "dist", "-l", "4173"]