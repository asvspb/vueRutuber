# Плагины

## Vuetify

[Vuetify](https://vuetifyjs.com/) - это компонентная библиотека Material Design для Vue.js.

### Настройка

Конфигурация Vuetify находится в файле `vuetify.ts`. В проекте настроена тема, которая использует цвета из переменных SCSS проекта:

- primary: `#409eff` (синий)
- secondary: `#093b86` (темно-синий)
- accent: `#42b983` (зеленый)

### Использование

Компоненты Vuetify можно использовать в любом компоненте Vue. Пример:

```vue
<template>
  <v-btn color="primary" @click="handleClick">Кнопка</v-btn>
  <v-card>
    <v-card-title>Заголовок карточки</v-card-title>
    <v-card-text>Содержимое карточки</v-card-text>
  </v-card>
</template>
```

### Стилизация

Компоненты Vuetify интегрированы с системой SCSS проекта. Можно использовать миксины и переменные из `src/styles/variables.scss` и `src/styles/mixins.scss` в сочетании с компонентами Vuetify.