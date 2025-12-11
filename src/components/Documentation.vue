<template>
  <section class="documentation">
    <h1>Документация учебного проекта</h1>
    
    <section class="documentation__section">
      <h2>Vue.js</h2>
      <p>Vue.js - это прогрессивный фреймворк для создания пользовательских интерфейсов. В отличие от монолитных фреймворков, Vue можно использовать как в отдельных частях приложения, так и для создания полноценных одностраничных приложений (SPA).</p>
      
      <h3>Основные концепции</h3>
      <ul>
        <li><strong>Компоненты</strong> - независимые и многократно используемые элементы пользовательского интерфейса</li>
        <li><strong>Реактивность</strong> - автоматическое обновление представления при изменении данных</li>
        <li><strong>Директивы</strong> - специальные атрибуты с префиксом v-</li>
        <li><strong>Жизненный цикл</strong> - хуки, позволяющие выполнять код на различных этапах жизни компонента</li>
      </ul>
      
      <h3>Примеры использования</h3>
      <div class="documentation__code">
        <pre><code>
// Объявление компонента (Options API — для сравнения)
export default {
  name: 'MyComponent',
  data() {
    return {
      message: 'Привет, Vue!'
    }
  },
  methods: {
    greet() {
      alert(this.message);
    }
  },
  computed: {
    reversedMessage() {
      return this.message.split('').reverse().join('');
    }
  }
}
        </code></pre>
      </div>
    </section>
    
    <section class="documentation__section">
      <h2>SCSS (Sass)</h2>
      <p>SCSS - это метаязык на основе CSS, который добавляет улучшения к стандартному CSS. Это позволяет писать более чистый, структурированный и поддерживаемый код стилей.</p>
      
      <h3>Основные возможности</h3>
      <ul>
        <li><strong>Переменные</strong> - хранение значений для многократного использования</li>
        <li><strong>Вложенность</strong> - структурирование CSS в соответствии с HTML</li>
        <li><strong>Миксины</strong> - многократно используемые блоки кода</li>
        <li><strong>Наследование</strong> - наследование стилей от других селекторов</li>
        <li><strong>Функции</strong> - выполнение вычислений в CSS</li>
      </ul>
      
      <h3>Примеры использования</h3>
      <div class="documentation__code">
        <pre><code>
// Переменные
$primary-color: #3498db;
$font-size: 16px;

// Миксин
@mixin button-style($bg-color) {
  background-color: $bg-color;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
}

// Использование
.my-button {
  @include button-style($primary-color);
  font-size: $font-size;
  
  &:hover {
    background-color: darken($primary-color, 10%);
  }
  
  .icon {
    margin-right: 8px;
  }
}
        </code></pre>
      </div>
    </section>
    
    <section class="documentation__section">
      <h2>SQLite</h2>
      <p>SQLite - это встраиваемая система управления реляционными базами данных, не требующая отдельного серверного процесса. В отличие от других СУБД, SQLite хранит всю базу данных, включая определения, таблицы, индексы и данные, в одном файле на обычной файловой системе.</p>
      
      <h3>Основные концепции</h3>
      <ul>
        <li><strong>Файловая база данных</strong> - вся база данных хранится в одном файле</li>
        <li><strong>Нет сервера</strong> - не требует отдельного процесса сервера</li>
        <li><strong>Легковесность</strong> - минимальные системные требования</li>
        <li><strong>Широкая совместимость</strong> - поддерживается во многих языках программирования</li>
      </ul>
      
      <h3>Примеры SQL-запросов</h3>
      <div class="documentation__code">
        <pre><code>
-- Создание таблицы
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Вставка данных
INSERT INTO users (name, email) VALUES ('Иван Иванов', 'ivan@example.com');

-- Выборка данных
SELECT id, name, email FROM users WHERE created_at > '2023-01-01';

-- Обновление данных
UPDATE users SET name = 'Иван Петров' WHERE id = 1;

-- Удаление данных
DELETE FROM users WHERE id = 1;
        </code></pre>
      </div>
    </section>
    
    <section class="documentation__section">
      <h2>Redis</h2>
      <p>Redis - это хранилище данных в оперативной памяти (in-memory data store), которое может использоваться в качестве базы данных, кэша и брокера сообщений. Он поддерживает различные структуры данных, такие как строки, хэши, списки, множества и др.</p>
      
      <h3>Основные возможности</h3>
      <ul>
        <li><strong>Ключ-значение хранилище</strong> - быстрый доступ к данным по ключу</li>
        <li><strong>Поддержка различных типов данных</strong> - строки, списки, множества, сортированные множества</li>
        <li><strong>Кэширование</strong> - временное хранение часто запрашиваемых данных</li>
        <li><strong>Публикация/подписка</strong> - реализация шаблона publish/subscribe</li>
        <li><strong>Сессии</strong> - хранение данных сессии пользователей</li>
      </ul>
      
      <h3>Примеры операций</h3>
      <div class="documentation__code">
        <pre><code>
// Установка и получение значения
SET user:100 "Иван Иванов"
GET user:100

// Работа со списками
LPUSH tasks "задача 1"
LPUSH tasks "задача 2"
LRANGE tasks 0 -1

// Работа с хэшами
HSET user:101 name "Петр Петров" email "petr@example.com"
HGETALL user:101

// Установка TTL (время жизни)
SETEX session:abc123 3600 "данные сессии"

// Сортированные множества
ZADD leaderboard 1000 "Игрок1"
ZADD leaderboard 1500 "Игрок2"
ZRANGE leaderboard 0 -1 WITHSCORES
        </code></pre>
      </div>
    </section>
  </section>
</template>

<script setup>
// Компонент статический, логики нет — используем `<script setup>` для единообразия
</script>

<style scoped lang="scss">
@use '../styles/variables.scss' as *;
@use '../styles/mixins.scss' as *;

.documentation {
  @include container(1200px);
  margin: 20px auto;
  padding: $padding-large;
  
  h1 {
    text-align: center;
    color: $primary-text-color;
    margin-bottom: $padding-large;
    @include responsive-font($font-size-xlarge, 32px);
  }
  
  &__section {
    margin-bottom: $padding-large;
    padding: $padding-large;
    border: 1px solid $border-color;
    border-radius: $border-radius;
    background-color: $background-color;
    @include shadow(1);
    
    h2 {
      color: $accent-color;
      margin-bottom: $padding-medium;
      padding-bottom: 10px;
      border-bottom: 2px solid $border-color;
    }
    
    h3 {
      color: $primary-text-color;
      margin: $padding-medium 0 $padding-small 0;
    }
    
    p {
      color: $secondary-text-color;
      line-height: 1.6;
      margin-bottom: $padding-medium;
    }
    
    ul {
      margin-left: $padding-large;
      margin-bottom: $padding-medium;
      
      li {
        margin-bottom: $padding-small;
        line-height: 1.5;
        
        strong {
          color: $primary-text-color;
        }
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
