<template>
  <v-dialog
    v-model="dialog"
    max-width="600"
  >
    <v-card>
      <v-card-title>
        <span class="text-h6">Import Rutube Playlist</span>
      </v-card-title>

      <v-card-text class="pt-4">
        <v-form ref="form" v-model="valid">
          <v-text-field
            v-model="playlistUrl"
            label="Rutube Playlist URL"
            placeholder="https://rutube.ru/plst/..."
            :rules="[rules.required, rules.validUrl]"
            required
            variant="underlined"
          ></v-text-field>

          <v-slider
            v-model="limit"
            label="Number of videos to import"
            :min="1"
            :max="100"
            :step="1"
            thumb-label="always"
            class="mt-4"
          >
            <template v-slot:append>
              <v-text-field
                v-model="limit"
                class="mt-n6"
                type="number"
                style="width: 80px"
                variant="outlined"
                density="compact"
                :rules="[rules.limitRange]"
              ></v-text-field>
            </template>
          </v-slider>
        </v-form>

        <v-alert
          v-if="importResult"
          :type="importResult.success ? 'success' : 'error'"
          variant="tonal"
          class="mt-4"
        >
          <div v-if="importResult.success">
            <div class="font-weight-bold">Import completed successfully!</div>
            <ul class="mt-2">
              <li>Imported: {{ importResult.data.imported }} videos</li>
              <li>Updated: {{ importResult.data.updated }} videos</li>
              <li>Linked: {{ importResult.data.linked }} videos</li>
            </ul>
          </div>
          <div v-else>
            {{ importResult.error }}
          </div>
        </v-alert>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          color="grey"
          variant="text"
          @click="closeDialog"
        >
          Cancel
        </v-btn>
        <v-btn
          color="primary"
          variant="elevated"
          @click="importPlaylist"
          :loading="loading"
          :disabled="!valid || loading"
        >
          Import
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { usePlaylistsStore } from '@/stores/playlists'

// Props
interface Props {
  modelValue: boolean
}
const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'import-complete': []
}>()

// Stores
const playlistsStore = usePlaylistsStore()

// Reactive variables
const playlistUrl = ref('')
const limit = ref(100)
const valid = ref(false)
const loading = ref(false)
const importResult = ref<any>(null)

// Form validation rules
const rules = {
  required: (value: string) => !!value || 'Required.',
  validUrl: (value: string) => {
    const urlPattern = /^https:\/\/rutube\.ru\/plst\/\d+\/?$/
    return urlPattern.test(value) || 'Must be a valid Rutube playlist URL (https://rutube.ru/plst/...).'
  },
  limitRange: (value: number) => {
    return value >= 1 && value <= 100 || 'Must be between 1 and 100.'
  }
}

// Computed properties
const dialog = computed({
  get() {
    return props.modelValue
  },
  set(value) {
    emit('update:modelValue', value)
  }
})

// Close dialog
const closeDialog = () => {
  dialog.value = false
  // Reset form
  playlistUrl.value = ''
  limit.value = 100
  importResult.value = null
}

// Import playlist
const importPlaylist = async () => {
  if (!valid.value) return

  loading.value = true
  importResult.value = null

  try {
    const result = await playlistsStore.importPlaylist(playlistUrl.value, limit.value)

    importResult.value = {
      success: true,
      data: result
    }

    // Emit event to notify parent of successful import
    setTimeout(() => {
      emit('import-complete')
      closeDialog()
    }, 1500)
  } catch (error: any) {
    console.error('Import error:', error)
    importResult.value = {
      success: false,
      error: error.message || 'Import failed'
    }
  } finally {
    loading.value = false
  }
}
</script>