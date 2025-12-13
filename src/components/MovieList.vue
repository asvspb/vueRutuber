<template>
  <div class="movie-list">
    <h2>Фильмы</h2>
    
    <div v-if="loading" class="loading">
      Загрузка...
    </div>
    
    <div v-else-if="error" class="error">
      Ошибка: {{ error.message || error }}
    </div>
    
    <div v-else class="movies-grid">
      <div 
        v-for="movie in movies" 
        :key="movie.id" 
        class="movie-card"
        @click="selectMovie(movie)"
      >
        <img 
          :src="movie.thumbnail_url || movie.image_url" 
          :alt="movie.title"
          class="movie-image"
          @error="onImageError"
        >
        <div class="movie-info">
          <h3 class="movie-title">{{ movie.title }}</h3>
          <p class="movie-year">Год: {{ movie.year }}</p>
          <p class="movie-views">Просмотры: {{ movie.views }}</p>
          <p class="movie-genre" v-if="movie.genre">Жанр: {{ movie.genre }}</p>
        </div>
      </div>
    
    <!-- Кнопки пагинации -->
    <div v-if="!loading && movies.length > 0" class="pagination">
      <button 
        @click="previousPage" 
        :disabled="currentPage === 0"
        class="pagination-btn"
      >
        Назад
      </button>
      <span class="page-info">Страница {{ currentPage + 1 }}</span>
      <button 
        @click="nextPage" 
        class="pagination-btn"
      >
        Вперед
      </button>
    </div>
  </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useMovies } from '../composables/useMovies.ts'

// Определяем пропсы
interface Props {
  limit?: number
}

const props = withDefaults(defineProps<Props>(), {
  limit: 10
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

const onImageError = (event: Event) => {
  const target = event.target as HTMLImageElement
  target.src = 'https://via.placeholder.com/300x400/cccccc/666666?text=Нет+изображения'
}

// Загружаем фильмы при монтировании компонента
onMounted(async () => {
  await fetchMovies()
})
</script>

<style scoped>
.movie-list {
  padding: 20px;
}

.loading, .error {
  text-align: center;
  padding: 20px;
  font-size: 18px;
}

.error {
  color: #f44336;
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.movie-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  background: white;
}

.movie-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.movie-image {
 width: 100%;
  height: 300px;
  object-fit: cover;
  display: block;
}

.movie-info {
  padding: 15px;
}

.movie-title {
 margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: bold;
  line-height: 1.3;
}

.movie-year,
.movie-views,
.movie-genre {
  margin: 5px 0;
  font-size: 14px;
 color: #666;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 20px;
}

.pagination-btn {
  padding: 8px 16px;
  border: 1px solid #ccc;
  background: white;
 border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background: #f5f5;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
}
</style>