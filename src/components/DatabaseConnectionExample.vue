<template>
  <div class="connection-examples">
    <h2>Примеры подключения к базам данных</h2>
    
    <div class="connection-examples__section">
      <h3>Подключение к SQLite</h3>
      <p>Для подключения к SQLite из Python-приложения (на сервере) используется SQLAlchemy:</p>
      
      <div class="connection-examples__code">
        <pre><code>
# Установка зависимости
pip install sqlalchemy aiosqlite

# Подключение в приложении
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Асинхронное подключение к базе данных SQLite
DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL)

# Создание сессии
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
);

# Функция для получения сессии базы данных
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
        
# Пример использования в эндпоинте FastAPI
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int, db: AsyncSession = Depends(get_db)):
    # Работа с базой данных
    pass
        </code></pre>
      </div>
    </div>
    
    <div class="connection-examples__section">
      <h3>Подключение к Redis</h3>
      <p>Для подключения к Redis из Node.js приложения используется библиотека redis:</p>
      
      <div class="connection-examples__code">
        <pre><code>
// Установка зависимости
npm install redis

// Подключение в приложении
const redis = require('redis');

// Создание клиента
const client = redis.createClient({
  host: 'localhost',
  port: 6379,
  // Дополнительные опции
  retry_strategy: (options) => {
    if (options.error && options.error.code === 'ECONNREFUSED') {
      console.error('Сервер Redis отклонил подключение');
      return new Error('Сервер Redis отклонил подключение');
    }
    if (options.total_retry_time > 1000 * 60 * 60) {
      console.error('Истекло время ожидания подключения к Redis');
      return new Error('Истекло время ожидания подключения к Redis');
    }
    if (options.attempt > 10) {
      console.error('Превышено количество попыток подключения к Redis');
      return undefined;
    }
    return Math.min(options.attempt * 100, 3000);
  }
});

// Подключение к Redis
client.connect().then(() => {
  console.log('Подключено к Redis');
}).catch((err) => {
  console.error('Ошибка подключения к Redis:', err);
});

// Примеры операций с Redis
const redisOperations = async () => {
  try {
    // Установка значения
    await client.set('user:100', JSON.stringify({ id: 100, name: 'John Doe', email: 'john@example.com' }));
    
    // Получение значения
    const user = await client.get('user:100');
    console.log('Пользователь:', JSON.parse(user));
    
    // Установка значения с TTL (временем жизни)
    await client.setEx('session:abc123', 3600, 'session_data_here');
    
    // Работа со списками
    await client.lPush('tasks', 'task1', 'task2', 'task3');
    const tasks = await client.lRange('tasks', 0, -1);
    console.log('Задачи:', tasks);
    
    // Увеличение числового значения
    await client.set('counter', 0);
    const newCounter = await client.incr('counter');
    console.log('Счетчик:', newCounter);
  } catch (error) {
    console.error('Ошибка операции Redis:', error);
  }
};

// Закрытие подключения
const closeRedisConnection = async () => {
  await client.quit();
};
        </code></pre>
      </div>
    </div>
    
    <div class="connection-examples__section">
      <h3>Практическое применение</h3>
      <p>В реальных приложениях MySQL и Redis часто используются вместе:</p>
      <ul>
        <li>MySQL: хранение основных данных с сохранением целостности</li>
        <li>Redis: кэширование частых запросов, сессии пользователей, очередь задач</li>
        <li>Пример архитектуры: приложение получает данные из MySQL, кэширует их в Redis на определенное время</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
// Статический компонент. Логика не требуется — используем `<script setup>` для единообразия.
</script>

<style scoped lang="scss">
@use '../styles/variables.scss' as *;
@use '../styles/mixins.scss' as *;

.connection-examples {
  @include container(1000px);
  margin: 20px auto;
  padding: $padding-large;
  
  h2 {
    color: $primary-text-color;
    text-align: center;
    margin-bottom: $padding-large;
    @include responsive-font($font-size-large, $font-size-xlarge);
  }
  
  &__section {
    margin-bottom: $padding-large;
    padding: $padding-medium;
    border: 1px solid $border-color;
    border-radius: $border-radius;
    background-color: $secondary-background;
    
    h3 {
      color: $accent-color;
      margin-bottom: $padding-small;
    }
    
    p {
      color: $secondary-text-color;
      margin-bottom: $padding-medium;
      line-height: 1.6;
    }
    
    ul {
      margin-left: $padding-large;
      margin-bottom: $padding-medium;
      
      li {
        margin-bottom: $padding-small;
        line-height: 1.5;
      }
    }
  }
  
  &__code {
    background-color: #2d2d2d;
    color: #f8f8f2;
    border-radius: $border-radius;
    padding: $padding-medium;
    margin: $padding-medium 0;
    overflow-x: auto;
    
    pre {
      margin: 0;
      font-size: $font-size-small;
    }
    
    code {
      font-family: 'Fira Code', 'Courier New', monospace;
    }
  }
}
</style>
