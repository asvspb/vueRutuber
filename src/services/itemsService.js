import api from './api.js'

export const itemsService = {
  // Получить все элементы
  async getAll() {
    const response = await api.get('/items')
    return response.data
  },

  // Получить элемент по ID
  async getById(id) {
    const response = await api.get(`/items/${id}`)
    return response.data
  },

  // Создать новый элемент
  async create(item) {
    const response = await api.post('/items', item)
    return response.data
  },

  // Обновить элемент
  async update(id, item) {
    const response = await api.put(`/items/${id}`, item)
    return response.data
  },

  // Удалить элемент
  async delete(id) {
    const response = await api.delete(`/items/${id}`)
    return response.data
  },
}