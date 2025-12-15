<template>
  <v-dialog v-model="dialog" max-width="640">
    <v-card>
      <v-card-title>
        <span class="text-h6">Import Rutube Channel</span>
      </v-card-title>
      <v-card-text class="pt-4">
        <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-4" />
        <v-form ref="form" v-model="valid">
          <v-text-field
            v-model="channelUrl"
            label="Rutube Channel URL"
            placeholder="https://rutube.ru/channel/32869212/"
            :rules="[rules.required, rules.validUrl]"
            required
            variant="underlined"
            class="mb-4"
          />

          <v-checkbox
            v-model="scanPlaylists"
            label="Scan playlists and import them"
            hide-details
            class="mb-2"
          />

          <v-row>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model.number="perPlaylistLimit"
                type="number"
                label="Per playlist limit"
                variant="outlined"
                density="comfortable"
                :rules="[rules.limitRange]"
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model.number="channelVideosLimit"
                type="number"
                label="Import last N channel videos (0 = skip)"
                variant="outlined"
                density="comfortable"
                :rules="[rules.nonNegative]"
              />
            </v-col>
          </v-row>
        </v-form>

        <v-alert v-if="importResult" :type="importResult.success ? 'success' : 'error'" variant="tonal" class="mt-2">
          <div v-if="importResult.success">
            <div class="font-weight-bold">Import completed successfully</div>
            <ul class="mt-2">
              <li>Channel: {{ importResult.data.title }} (id: {{ importResult.data.rutube_channel_id }})</li>
              <li>Imported videos: {{ importResult.data.imported_videos }}</li>
              <li v-if="importResult.data.playlists_found !== undefined">Playlists found: {{ importResult.data.playlists_found }}</li>
              <li v-if="importResult.data.playlists_imported !== undefined">Playlists imported: {{ importResult.data.playlists_imported }}</li>
            </ul>
          </div>
          <div v-else>
            {{ importResult.error }}
          </div>
        </v-alert>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="grey" variant="text" @click="closeDialog">Cancel</v-btn>
        <v-btn color="primary" variant="elevated" @click="importChannel" :loading="loading" :disabled="!valid || loading">
          Import
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useChannelsStore } from '@/stores/channels'
import { useNotify } from '@/composables/useNotify'

interface Props { modelValue: boolean }
const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'import-complete': []
}>()

const channelsStore = useChannelsStore()

const channelUrl = ref('')
const scanPlaylists = ref(true)
const perPlaylistLimit = ref(100)
const channelVideosLimit = ref(Number((import.meta as any).env?.VITE_DEFAULT_CHANNEL_VIDEOS_LIMIT ?? 20))
const valid = ref(false)
const loading = ref(false)
const importResult = ref<any>(null)
const notify = useNotify()

const rules = {
  required: (v: string) => !!v || 'Required.',
  validUrl: (v: string) => {
    const re = /^https:\/\/rutube\.ru\/channel\/\d+\/?$/
    return re.test(v) || 'Must be a valid Rutube channel URL (https://rutube.ru/channel/{id}/)'
  },
  limitRange: (v: number) => (v >= 1 && v <= 1000) || 'Must be between 1 and 1000.',
  nonNegative: (v: number) => (v >= 0) || 'Must be >= 0.'
}

const dialog = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value)
})

const closeDialog = () => {
  dialog.value = false
  // Reset
  channelUrl.value = ''
  scanPlaylists.value = true
  perPlaylistLimit.value = 100
  channelVideosLimit.value = 0
  importResult.value = null
}

const importChannel = async () => {
  if (!valid.value) return
  loading.value = true
  importResult.value = null
  try {
    const result = await channelsStore.importChannel(channelUrl.value, {
      scan_playlists: scanPlaylists.value,
      per_playlist_limit: perPlaylistLimit.value,
      channel_videos_limit: channelVideosLimit.value,
    })
    importResult.value = { success: true, data: result }
    notify.success(`Channel imported: ${result.title}. Videos: ${result.imported_videos}${result.playlists_imported !== undefined ? ", playlists: " + result.playlists_imported : ''}`)
    setTimeout(() => {
      emit('import-complete')
      closeDialog()
    }, 1200)
  } catch (e: any) {
    importResult.value = { success: false, error: e?.message || 'Import failed' }
    notify.error(importResult.value.error)
  } finally {
    loading.value = false
  }
}
</script>
