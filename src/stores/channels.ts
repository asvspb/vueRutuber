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

  const importChannel = async (url: string, options?: { scan_playlists?: boolean; per_playlist_limit?: number; channel_videos_limit?: number }) => {
    loading.value = true
    error.value = null
    try {
      const params = new URLSearchParams()
      params.set('rutube_channel_url', url)
      if (options?.channel_videos_limit !== undefined) params.set('channel_videos_limit', String(options.channel_videos_limit))
      if (options?.scan_playlists !== undefined) params.set('scan_playlists', String(options.scan_playlists))
      if (options?.per_playlist_limit !== undefined) params.set('per_playlist_limit', String(options.per_playlist_limit))

      const response = await fetch(`/api/channels/import?${params.toString()}`, { method: 'POST' })
      if (!response.ok) {
        const err = await response.json().catch(() => ({}))
        throw new Error(err.detail || `HTTP ${response.status}`)
      }
      const result = await response.json()
      await fetchChannels()
      return result
    } catch (err) {
      console.error('Error importing channel:', err)
      error.value = err instanceof Error ? err.message : 'Import failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    channels,
    selectedChannelId,
    loading,
    error,
    fetchChannels,
    selectChannel,
    importChannel
  }
})