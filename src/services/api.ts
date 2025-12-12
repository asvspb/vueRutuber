import axios from 'axios'

// Создание экземпляра Axios
const api = axios.create({
  baseURL: (import.meta.env as any).VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Интерсептор запросов
api.interceptors.request.use(
  (config) => {
    // Добавление токена авторизации, если есть
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Интерсептор ответов
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Обработка неавторизованного доступа
      localStorage.removeItem('authToken')
      // Можно добавить редирект на страницу логина
    }
    return Promise.reject(error)
  }
)

export default api