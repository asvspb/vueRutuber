# Многоэтапная сборка Vite+Vue SPA

# Этап 1: сборка фронтенда
FROM node:18-alpine AS builder

WORKDIR /app

# Установим зависимости
COPY package*.json ./
RUN npm ci

# Копируем исходники и собираем
COPY . .
RUN npm run build

# Этап 2: легкий образ для отдачи статики через serve
FROM node:18-alpine AS runner

WORKDIR /app

# Копируем только прод-артефакты и файлы, нужные для запуска
COPY package*.json ./
COPY --from=builder /app/dist ./dist

# Устанавливаем prod-зависимости и serve для отдачи статики
RUN npm install --only=production && npm install -g serve

# Порт для доступа к приложению
ENV PORT=4173
EXPOSE 4173

# Команда запуска: отдача статики через serve
CMD ["serve", "-s", "dist", "-l", "4173"]