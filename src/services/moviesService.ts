import api from './api.js'

export const moviesService = {
  // Получить все фильмы
  async getAll(skip: number = 0, limit: number = 10) {
    const response = await api.get('/movies', { params: { skip, limit } })
    return response.data
 },

  // Получить фильм по ID
  async getById(id: string | number) {
    const response = await api.get(`/movies/${id}`)
    return response.data
  },

  // Создать новый фильм
  async create(movie: any) {
    const response = await api.post('/movies', movie)
    return response.data
  },

  // Обновить фильм
  async update(id: string | number, movie: any) {
    const response = await api.put(`/movies/${id}`, movie)
    return response.data
 },

  // Удалить фильм
 async delete(id: string | number) {
    const response = await api.delete(`/movies/${id}`)
    return response.data
  },

  // Получить фильмы по году
  async getByYear(year: number, skip: number = 0, limit: number = 100) {
    const response = await api.get(`/movies/year/${year}`, { params: { skip, limit } })
    return response.data
  },

  // Получить фильмы по жанру
 async getByGenre(genre: string, skip: number = 0, limit: number = 100) {
    const response = await api.get(`/movies/genre/${genre}`, { params: { skip, limit } })
    return response.data
  },

  // Увеличить количество просмотров
  async incrementViews(id: string | number) {
    const response = await api.post(`/movies/${id}/increment-views`)
    return response.data
  }
}