<template>
  <v-container fluid class="movie-list pa-4">
    <v-row class="mb-4">
      <v-col>
        <h2 class="text-h4 font-weight-bold">🎬 Фильмы с Rutube</h2>
        <p class="text-subtitle-1 text-grey">Всего загружено: {{ movies.length }} фильмов</p>
      </v-col>
    </v-row>

    <!-- Загрузка -->
    <v-row v-if="loading" justify="center" class="my-10">
      <v-col cols="auto">
        <v-progress-circular
          indeterminate
          color="primary"
          size="64"
        ></v-progress-circular>
        <p class="text-center mt-4">Загрузка фильмов...</p>
      </v-col>
    </v-row>

    <!-- Ошибка -->
    <v-alert
      v-else-if="error"
      type="error"
      variant="tonal"
      class="mb-4"
    >
      <v-alert-title>Ошибка загрузки</v-alert-title>
      {{ error.message || error }}
    </v-alert>

    <!-- Сетка фильмов -->
    <v-row v-else>
      <v-col
        v-for="movie in movies"
        :key="movie.id"
        cols="12"
        sm="6"
        md="4"
        lg="3"
        xl="2"
      >
        <v-card
          class="movie-card h-100"
          elevation="2"
          hover
          @click="selectMovie(movie)"
        >
          <v-img
            :src="movie.thumbnail_url || movie.image_url"
            :alt="movie.title"
            height="200"
            cover
            class="bg-grey-lighten-2"
          >
            <template v-slot:error>
              <v-img
                src="https://via.placeholder.com/300x200/cccccc/666666?text=Нет+изображения"
                height="200"
                cover
              ></v-img>
            </template>
          </v-img>

          <v-card-title class="text-subtitle-1 font-weight-bold text-wrap">
            {{ movie.title }}
          </v-card-title>

          <v-card-text class="pb-2">
            <div class="d-flex flex-column gap-1">
              <v-chip
                v-if="movie.year"
                size="small"
                color="primary"
                variant="tonal"
                class="mr-1"
              >
                <v-icon start size="small">mdi-calendar</v-icon>
                {{ movie.year }}
              </v-chip>

              <v-chip
                v-if="movie.genre"
                size="small"
                color="secondary"
                variant="tonal"
                class="mr-1"
              >
                <v-icon start size="small">mdi-tag</v-icon>
                {{ movie.genre }}
              </v-chip>

              <div class="text-caption text-grey mt-2">
                <v-icon size="small" class="mr-1">mdi-eye</v-icon>
                {{ formatViews(movie.views) }} просмотров
              </div>

              <div v-if="movie.duration" class="text-caption text-grey">
                <v-icon size="small" class="mr-1">mdi-clock-outline</v-icon>
                {{ movie.duration }}
              </div>

              <div v-if="movie.channel_added_at" class="text-caption text-grey">
                <v-icon size="small" class="mr-1">mdi-calendar-plus</v-icon>
                {{ formatDate(movie.channel_added_at) }}
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Пагинация -->
    <v-row v-if="!loading && movies.length > 0" justify="center" class="mt-6">
      <v-col cols="auto">
        <v-btn
          variant="outlined"
          color="primary"
          class="mr-2"
          :disabled="currentPage === 0"
          @click="previousPage"
        >
          <v-icon start>mdi-chevron-left</v-icon>
          Назад
        </v-btn>

        <v-chip color="primary" variant="flat" class="mx-2">
          Страница {{ currentPage + 1 }}
        </v-chip>

        <v-btn
          variant="outlined"
          color="primary"
          class="ml-2"
          @click="nextPage"
        >
          Вперед
          <v-icon end>mdi-chevron-right</v-icon>
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useMovies } from '../composables/useMovies.ts'

// Определяем пропсы
interface Props {
  limit?: number
}

const props = withDefaults(defineProps<Props>(), {
  limit: 100
})

// Определяем emit
const emit = defineEmits<{
  movieSelected: [movie: any]
}>()

// Используем композабл
const {
  movies,
  loading,
  error,
  fetchMovies
} = useMovies({ limit: props.limit })

// Состояние пагинации
const currentPage = ref(0)
const itemsPerPage = ref(props.limit)

// Функции
const selectMovie = (movie: any) => {
  emit('movieSelected', movie)
}

const nextPage = async () => {
  currentPage.value++
  await fetchMovies(currentPage.value * itemsPerPage.value, itemsPerPage.value)
}

const previousPage = async () => {
  if (currentPage.value > 0) {
    currentPage.value--
    await fetchMovies(currentPage.value * itemsPerPage.value, itemsPerPage.value)
  }
}

// Форматирование просмотров
const formatViews = (views: number | null | undefined): string => {
  if (!views) return '0'
  if (views >= 1000000) {
    return (views / 1000000).toFixed(1) + 'M'
  }
  if (views >= 1000) {
    return (views / 1000).toFixed(1) + 'K'
  }
  return views.toString()
}

// Форматирование даты добавления
const formatDate = (dateString: string | null | undefined): string => {
  if (!dateString) return ''

  const date = new Date(dateString)

  // Проверка валидности даты
  if (isNaN(date.getTime())) return ''

  // Форматирование: "15 дек 2024"
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

// Загружаем фильмы при монтировании компонента
onMounted(async () => {
  await fetchMovies()
})
</script>

<style scoped>
.movie-card {
  cursor: pointer;
  transition: transform 0.2s ease-in-out;
}

.movie-card:hover {
  transform: translateY(-4px);
}

.text-wrap {
  word-break: break-word;
  white-space: normal;
  line-height: 1.3;
}

.h-100 {
  height: 100%;
}

.gap-1 {
  gap: 4px;
}
</style>