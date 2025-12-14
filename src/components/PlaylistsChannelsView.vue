<template>
  <v-container fluid class="pa-0">
    <!-- Top Channels Bar -->
    <TopChannelsBar 
      v-model="selectedChannelId"
      @update:model-value="handleChannelChange"
    />

    <v-divider></v-divider>

    <v-row no-gutters>
      <!-- Sidebar Playlists -->
      <v-col cols="auto">
        <SidebarPlaylists 
          v-model="selectedPlaylistId"
          @update:model-value="handlePlaylistChange"
        />
      </v-col>

      <!-- Main Content Area -->
      <v-col class="d-flex">
        <v-container fluid class="pa-4">
          <VideoGrid 
            :playlist-id="selectedPlaylistId"
            :channel-id="selectedChannelId"
          />
        </v-container>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import SidebarPlaylists from './SidebarPlaylists.vue'
import TopChannelsBar from './TopChannelsBar.vue'
import VideoGrid from './VideoGrid.vue'

// Props
interface Props {
  playlistId?: number | null
  channelId?: number | null
}
const props = withDefaults(defineProps<Props>(), {
  playlistId: null,
  channelId: null
})

// Router
const router = useRouter()

// Reactive variables
const selectedPlaylistId = ref<number | null>(props.playlistId)
const selectedChannelId = ref<number | null>(props.channelId)

// Sync props to reactive vars
watch(() => props.playlistId, (newVal) => {
  selectedPlaylistId.value = newVal
})
watch(() => props.channelId, (newVal) => {
  selectedChannelId.value = newVal
})

// Handle playlist change
const handlePlaylistChange = (id: number | null) => {
  selectedPlaylistId.value = id
  updateRoute()
}

// Handle channel change
const handleChannelChange = (id: number | null) => {
  selectedChannelId.value = id
  updateRoute()
}

// Update route based on selections
const updateRoute = () => {
  const query: any = {}
  if (selectedChannelId.value) {
    query.channelId = selectedChannelId.value.toString()
  }
  router.push({
    name: 'Playlists',
    params: {
      playlistId: selectedPlaylistId.value || undefined
    },
    query
  })
}
</script>

<style scoped>
.v-container {
  height: 100vh;
}
</style>