import { ref } from 'vue'
import api from '../services/api.ts'

interface ApiOptions {
  method?: string
  params?: Record<string, any>
  data?: any
  immediate?: boolean
}

export function useApi(endpoint: string, options: ApiOptions = {}) {
  const {
    method = 'get',
    params = {},
    data: requestData = null,
    immediate = false
  } = options

  const loading = ref(false)
  const error = ref<any>(null)
  const data = ref<any>(null)

  const execute = async (overrideOptions: Partial<ApiOptions> = {}) => {
    const {
      method: overrideMethod = method,
      params: overrideParams = params,
      data: overrideData = requestData
    } = overrideOptions

    loading.value = true
    error.value = null

    try {
      const response = await api({
        method: overrideMethod,
        url: endpoint,
        params: overrideParams,
        data: overrideData
      })
      data.value = response.data
      return response.data
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  if (immediate) {
    execute()
  }

  return {
    data,
    loading,
    error,
    execute
  }
}

// Специфические хуки для CRUD операций
export function useFetchItems() {
  return useApi('/items', { immediate: true })
}

export function useCreateItem() {
  return useApi('/items', { method: 'post' })
}

export function useUpdateItem(id: string | number) {
  return useApi(`/items/${id}`, { method: 'put' })
}

export function useDeleteItem(id: string | number) {
  return useApi(`/items/${id}`, { method: 'delete' })
}
