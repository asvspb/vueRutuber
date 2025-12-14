<template>
  <v-container>
    <v-row v-if="videosStore.loading" justify="center" class="mt-10">
      <v-col cols="12" class="text-center">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </v-col>
    </v-row>

    <v-row v-else-if="videosStore.error" justify="center" class="mt-10">
      <v-col cols="12" class="text-center">
        <v-alert type="error" variant="tonal">
          {{ videosStore.error }}
          <v-alert-actions>
            <v-btn @click="fetchVideos" variant="text">Retry</v-btn>
          </v-alert-actions>
        </v-alert>
      </v-col>
    </v-row>

    <v-row v-else-if="!videosStore.videos.length" justify="center" class="mt-10">
      <v-col cols="12" class="text-center">
        <v-alert type="info" variant="tonal">
          No videos found. Select a playlist or try a different filter.
        </v-alert>
      </v-col>
    </v-row>

    <v-row v-else>
      <v-col
        v-for="movie in videosStore.videos"
        :key="movie.id"
        cols="12"
        sm="6"
        md="4"
        lg="3"
      >
        <v-card class="movie-card">
          <v-img
            :src="movie.thumbnail_url"
            height="200px"
            cover
          ></v-img>

          <v-card-title class="text-subtitle-1 py-2">
            {{ movie.title }}
          </v-card-title>

          <v-card-subtitle class="pb-1">
            <div class="d-flex align-center">
              <v-icon size="small" class="mr-1">mdi-calendar</v-icon>
              {{ formatDate(movie.channel_added_at) }}
            </div>
          </v-card-subtitle>

          <v-card-text class="pb-2 pt-1 text-caption">
            <div class="d-flex justify-space-between">
              <div>
                <v-chip size="x-small" label variant="outlined" class="mr-1">
                  {{ movie.year }}
                </v-chip>
                <v-chip size="x-small" label variant="outlined">
                  {{ movie.genre }}
                </v-chip>
              </div>
              <div class="d-flex align-center">
                <v-icon size="small" class="mr-1">mdi-eye</v-icon>
                <span>{{ formatViews(movie.views) }}</span>
              </div>
            </div>
            <div class="mt-1 d-flex align-center">
              <v-icon size="small" class="mr-1">mdi-clock-outline</v-icon>
              <span>{{ movie.duration }}</span>
            </div>
          </v-card-text>

          <v-card-actions>
            <v-btn
              :href="movie.source_url"
              target="_blank"
              variant="text"
              size="small"
              prepend-icon="mdi-play"
            >
              Watch
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- Load more button if there are more items -->
    <v-row v-if="!videosStore.loading && videosStore.videos.length > 0" justify="center" class="my-4">
      <v-col cols="auto">
        <v-btn
          v-if="videosStore.hasMore"
          @click="loadMore"
          :loading="videosStore.loadingMore"
          variant="outlined"
        >
          Load More
          <v-icon end>mdi-chevron-down</v-icon>
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useVideosStore } from '@/stores/videos'

// Props
interface Props {
  playlistId?: number | null
  channelId?: number | null
}
const props = withDefaults(defineProps<Props>(), {
  playlistId: null,
  channelId: null
})

// Stores
const videosStore = useVideosStore()

// Format date
const formatDate = (dateString: string | null) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return ''
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

// Format views
const formatViews = (views: number) => {
  if (views >= 1000000) {
    return `${(views / 1000000).toFixed(1)}M`
  }
  if (views >= 1000) {
    return `${(views / 1000).toFixed(1)}K`
  }
  return views.toString()
}

// Fetch videos
const fetchVideos = () => {
  videosStore.fetchVideos()
}

// Load more videos
const loadMore = () => {
  videosStore.loadMore()
}

// Handle prop changes
watch([() => props.playlistId, () => props.channelId], ([newPlaylistId, newChannelId]) => {
  videosStore.setFilters(newPlaylistId, newChannelId)
}, { deep: true })

// Initialize
onMounted(() => {
  videosStore.setFilters(props.playlistId, props.channelId)
})
</script>

<style scoped>
.movie-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style>