<template>
  <v-navigation-drawer
    v-model="drawer"
    :rail="rail"
    permanent
    @click="rail = false"
  >
    <v-list density="compact" nav>
      <v-list-item
        prepend-icon="mdi-playlist-play"
        title="Playlists"
        value="playlists"
        class="mb-2"
      ></v-list-item>

      <v-divider class="mb-4"></v-divider>

      <div v-for="playlist in playlistsStore.playlists" :key="playlist.id">
        <v-list-item
          :value="playlist.id"
          :class="{ 'active-playlist': playlistsStore.selectedPlaylistId === playlist.id }"
          @click="selectPlaylist(playlist.id)"
        >
          <template v-slot:prepend>
            <v-icon>mdi-playlist-music</v-icon>
          </template>
          <v-list-item-title>{{ playlist.title }}</v-list-item-title>
          <template v-slot:append>
            <v-badge :content="playlist.videos_count" inline></v-badge>
          </template>
        </v-list-item>
      </div>

      <v-list-item
        prepend-icon="mdi-plus"
        title="Import Playlist"
        value="import"
        class="mt-4"
        @click="showImportDialog = true"
      ></v-list-item>
    </v-list>

    <v-divider></v-divider>

    <template v-slot:append>
      <v-list density="compact" nav>
        <v-list-item @click="toggleRail">
          <v-icon :icon="rail ? 'mdi-chevron-right' : 'mdi-chevron-left'"></v-icon>
        </v-list-item>
      </v-list>
    </template>
  </v-navigation-drawer>

  <!-- Import Dialog -->
  <PlaylistImportDialog
    v-model="showImportDialog"
    @import-complete="handleImportComplete"
  />
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { usePlaylistsStore } from '@/stores/playlists'
import PlaylistImportDialog from './PlaylistImportDialog.vue'

// Props
interface Props {
  modelValue?: number | null
}
const props = withDefaults(defineProps<Props>(), {
  modelValue: null
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: number | null]
}>()

// Stores
const playlistsStore = usePlaylistsStore()

// Reactive variables
const drawer = ref(true)
const rail = ref(true)
const showImportDialog = ref(false)

// Toggle rail mode
const toggleRail = () => {
  rail.value = !rail.value
}

// Select playlist
const selectPlaylist = (id: number) => {
  playlistsStore.selectPlaylist(id)
  emit('update:modelValue', id)
}

// Handle import completion
const handleImportComplete = () => {
  // This will be handled by the dialog itself
  showImportDialog.value = false
}

// Watch for changes in selected playlist
watch(() => props.modelValue, (newVal) => {
  playlistsStore.selectPlaylist(newVal)
})

// Initialize
onMounted(async () => {
  await playlistsStore.fetchPlaylists()
  // Set the selected playlist from props if not already set
  if (props.modelValue !== null && props.modelValue !== playlistsStore.selectedPlaylistId) {
    playlistsStore.selectPlaylist(props.modelValue)
  }
})
</script>

<style scoped>
.active-playlist {
  background-color: rgba(0, 0, 0, 0.1);
}
</style>