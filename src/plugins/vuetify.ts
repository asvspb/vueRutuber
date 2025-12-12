import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

// Импортируем иконки Material Design
import '@mdi/font/css/materialdesignicons.css'

// Определяем тему на основе существующих переменных проекта
export default createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          // Используем основные цвета из переменных проекта
          primary: '#409eff',    // $button-primary-bg
          secondary: '#093b86',  // $button-secondary-bg
          accent: '#42b983',     // $accent-color
          error: '#dc3545',
          info: '#2196F3',
          success: '#4CAF50',
          warning: '#FFC107',
          background: '#ffffff', // $background-color
          surface: '#ffffff',
          'on-surface': '#2c3e50', // $primary-text-color
        }
      }
    }
  },
  defaults: {
    // Устанавливаем базовые настройки компонентов
    VBtn: {
      style: 'text-transform: none;', // Отключаем автоматическое преобразование текста кнопок
    },
  }
})