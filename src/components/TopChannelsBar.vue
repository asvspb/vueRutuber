<template>
  <v-container fluid class="py-2 px-4">
    <v-row align="center" no-gutters>
      <v-col>
        <v-slide-group
          v-model="channelsStore.selectedChannelId"
          class="pa-2"
          show-arrows
          @change="handleChannelChange"
        >
          <v-slide-group-item
            v-for="channel in channelsStore.channels"
            :key="channel.id"
            v-slot="{ isSelected }"
            :value="channel.id"
          >
            <v-chip
              :class="{ 'active-channel': isSelected }"
              :color="isSelected ? 'primary' : 'default'"
              :variant="isSelected ? 'flat' : 'outlined'"
              class="ma-1"
            >
              <v-avatar start :image="channel.avatar_url" size="24"></v-avatar>
              {{ channel.title }}
              <v-badge
                :content="channel.videos_count"
                color="grey"
                class="ml-1"
                inline
              ></v-badge>
            </v-chip>
          </v-slide-group-item>
        </v-slide-group>
      </v-col>

      <v-col cols="auto" class="d-flex align-center">
        <v-btn
          icon="mdi-plus"
          variant="text"
          density="comfortable"
          class="mr-1"
          @click="showImportDialog = true"
        >
          <v-icon>mdi-plus</v-icon>
          <v-tooltip activator="parent" location="bottom">Import Channel</v-tooltip>
        </v-btn>
        <v-btn
          icon="mdi-close"
          variant="text"
          density="comfortable"
          @click="clearChannelFilter"
          :disabled="!channelsStore.selectedChannelId"
        >
          <v-icon>mdi-close</v-icon>
          <v-tooltip activator="parent" location="bottom">Clear filter</v-tooltip>
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
  <ChannelImportDialog v-model="showImportDialog" @import-complete="handleImportComplete" />
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useChannelsStore } from '@/stores/channels'
import ChannelImportDialog from './ChannelImportDialog.vue'
import { usePlaylistsStore } from '@/stores/playlists'

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
const channelsStore = useChannelsStore()
const playlistsStore = usePlaylistsStore()
const showImportDialog = ref(false)

// Handle channel change
const handleChannelChange = () => {
  emit('update:modelValue', channelsStore.selectedChannelId)
}

// Clear channel filter
const clearChannelFilter = () => {
  channelsStore.selectChannel(null)
  emit('update:modelValue', null)
}

// Initialize
const handleImportComplete = async () => {
  await channelsStore.fetchChannels()
  await playlistsStore.fetchPlaylists()
}

onMounted(async () => {
  await channelsStore.fetchChannels()
  // Set the selected channel from props if not already set
  if (props.modelValue !== null && props.modelValue !== channelsStore.selectedChannelId) {
    channelsStore.selectChannel(props.modelValue)
  }
})
</script>

<style scoped>
.active-channel {
  border: 2px solid #1976d2 !important;
}
</style>