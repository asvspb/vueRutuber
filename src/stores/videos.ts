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

export interface Movie {
  id: number
  title: string
  year: number
  image_url?: string
  thumbnail_url?: string
  views: number
  added_at?: string
  channel_added_at?: string
  source_url: string
  duration: string
  description: string
  genre: string
  rating?: number
  is_active: boolean
  channel_id: number
  rutube_video_id?: string
  channel?: Channel
}

export const useVideosStore = defineStore('videos', () => {
  const videos = ref<Movie[]>([])
  const loading = ref(false)
  const loadingMore = ref(false)
  const error = ref<string | null>(null)
  const skip = ref(0)
  const limit = ref(24)
  const hasMore = ref(true)
  const playlistId = ref<number | null>(null)
  const channelId = ref<number | null>(null)

  const fetchVideos = async (reset = true) => {
    if (!playlistId.value) {
      videos.value = []
      hasMore.value = false
      return
    }

    if (reset) {
      loading.value = true
      skip.value = 0
      videos.value = []
    } else {
      loadingMore.value = true
    }

    error.value = null

    try {
      // Build query string
      let queryString = `?skip=${skip.value}&limit=${limit.value}&order=-channel_added_at`
      if (channelId.value) {
        queryString += `&channelId=${channelId.value}`
      }

      const response = await fetch(`/api/playlists/${playlistId.value}/videos${queryString}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      if (reset) {
        videos.value = data
      } else {
        videos.value = [...videos.value, ...data]
      }

      // Check if there are more items
      hasMore.value = data.length === limit.value

    } catch (err) {
      console.error('Error fetching videos:', err)
      error.value = 'Failed to fetch videos'
    } finally {
      loading.value = false
      loadingMore.value = false
    }
  }

  const setFilters = (newPlaylistId: number | null, newChannelId: number | null) => {
    if (playlistId.value !== newPlaylistId || channelId.value !== newChannelId) {
      playlistId.value = newPlaylistId
      channelId.value = newChannelId
      fetchVideos()
    }
  }

  const loadMore = () => {
    if (hasMore.value && !loadingMore.value) {
      skip.value += limit.value
      fetchVideos(false)
    }
  }

  return {
    videos,
    loading,
    loadingMore,
    error,
    hasMore,
    fetchVideos,
    setFilters,
    loadMore
  }
})