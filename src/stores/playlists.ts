import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Playlist {
  id: number
  rutube_id: string
  title: string
  description?: string
  image_url?: string
  is_active: boolean
  created_at: string
  videos_count: number
}

export const usePlaylistsStore = defineStore('playlists', () => {
  const playlists = ref<Playlist[]>([])
  const selectedPlaylistId = ref<number | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchPlaylists = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await fetch('/api/playlists/')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      playlists.value = await response.json()
    } catch (err) {
      console.error('Error fetching playlists:', err)
      error.value = 'Failed to fetch playlists'
    } finally {
      loading.value = false
    }
  }

  const selectPlaylist = (id: number | null) => {
    selectedPlaylistId.value = id
  }

  const importPlaylist = async (url: string, limit: number = 100) => {
    loading.value = true
    error.value = null
    try {
      const response = await fetch('/api/playlists/import', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          rutube_playlist_url: url,
          limit
        })
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Import failed')
      }
      
      const result = await response.json()
      
      // Refresh playlists after successful import
      await fetchPlaylists()
      
      // Set the newly imported playlist as selected if it's available
      if (result.playlist_id) {
        selectPlaylist(result.playlist_id)
      }
      
      return result
    } catch (err) {
      console.error('Error importing playlist:', err)
      error.value = err instanceof Error ? err.message : 'Import failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    playlists,
    selectedPlaylistId,
    loading,
    error,
    fetchPlaylists,
    selectPlaylist,
    importPlaylist
  }
})