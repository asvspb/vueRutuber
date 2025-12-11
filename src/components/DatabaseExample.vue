<template>
  <section class="database">
    <h2>Примеры работы с базами данных</h2>
    
    <div class="database__section">
      <h3>SQLite</h3>
      <p>SQLite - это встраиваемая система управления реляционными базами данных, не требующая отдельного серверного процесса.</p>
      <div class="database__code">
        <pre><code>
// Пример подключения к SQLite с использованием SQLAlchemy (на стороне сервера)
import sqlite3
from sqlalchemy import create_engine, text

# Создание подключения к базе данных SQLite
engine = create_engine("sqlite:///./test.db")

# Пример выполнения SQL-запроса
with engine.connect() as connection:
    result = connection.execute(text("SELECT 1"))
    print(result.fetchone())
        </code></pre>
      </div>
    </div>
    
    <div class="database__section">
      <h3>Redis</h3>
      <p>Redis - это распределенное хранилище данных в оперативной памяти, часто используемое в качестве кэша, базы данных и брокера сообщений.</p>
      <div class="database__code">
        <pre><code>
// Пример подключения к Redis (на стороне сервера)
const redis = require('redis');

const client = redis.createClient({
  host: 'localhost',
  port: 6379
});

client.on('connect', () => {
  console.log('Подключено к Redis');
});

client.on('error', (err) => {
  console.error('Ошибка Redis:', err);
});
        </code></pre>
      </div>
    </div>
    
    <DatabaseConnectionExample />
  </section>
</template>

<script setup>
import DatabaseConnectionExample from './DatabaseConnectionExample.vue'
</script>

<style scoped lang="scss">
@use '../styles/variables.scss' as *;

.database {
  margin: 20px auto;
  padding: 20px;
  width: 80%;
  
  h2 {
    color: $primary-text-color;
    border-bottom: 2px solid $accent-color;
    padding-bottom: 10px;
  }
  
  &__section {
    margin: 30px 0;
    
    h3 {
      color: $accent-color;
      margin-bottom: 15px;
    }
    
    p {
      color: $secondary-text-color;
      line-height: 1.6;
    }
  }
  
  &__code {
    background-color: $secondary-background;
    border: 1px solid $border-color;
    border-radius: $border-radius;
    padding: $padding-medium;
    margin-top: 15px;
    overflow-x: auto;
    
    pre {
      margin: 0;
      font-size: $font-size-small;
      
      code {
        color: #333;
      }
    }
  }
}
</style>
