import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Channel {
  id: number
  rutube_id: string
  title: string
  description?: string
  avatar_url?: string
  is_active: boolean
  created_at: string
  videos_count: number
}

export const useChannelsStore = defineStore('channels', () => {
  const channels = ref<Channel[]>([])
  const selectedChannelId = ref<number | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchChannels = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await fetch('/api/channels/')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      channels.value = await response.json()
    } catch (err) {
      console.error('Error fetching channels:', err)
      error.value = 'Failed to fetch channels'
    } finally {
      loading.value = false
    }
  }

  const selectChannel = (id: number | null) => {
    selectedChannelId.value = id
  }

  return {
    channels,
    selectedChannelId,
    loading,
    error,
    fetchChannels,
    selectChannel
  }
})