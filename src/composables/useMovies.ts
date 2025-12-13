import { ref } from 'vue'
import { moviesService } from '../services/moviesService.ts'

interface Movie {
  id: number
  title: string
  year: number
  image_url: string
  thumbnail_url: string | null
  views: number
  added_at: string
  source_url: string | null
  duration: string | null
  description: string | null
  genre: string | null
  rating: number | null
  is_active: boolean
}

interface ApiOptions {
  skip?: number
  limit?: number
 year?: number
 genre?: string
}

export function useMovies(options: ApiOptions = {}) {
  const { skip = 0, limit = 10 } = options

  const loading = ref(false)
  const error = ref<any>(null)
  const movies = ref<Movie[]>([])
  const currentMovie = ref<Movie | null>(null)

  const fetchMovies = async (fetchSkip?: number, fetchLimit?: number) => {
    loading.value = true
    error.value = null

    try {
      const response = await moviesService.getAll(fetchSkip || skip, fetchLimit || limit)
      movies.value = response
      return response
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchMovieById = async (id: string | number) => {
    loading.value = true
    error.value = null

    try {
      const response = await moviesService.getById(id)
      currentMovie.value = response
      return response
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

 const createMovie = async (movieData: Partial<Movie>) => {
    loading.value = true
    error.value = null

    try {
      const response = await moviesService.create(movieData)
      movies.value.unshift(response)
      return response
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

 const updateMovie = async (id: string | number, movieData: Partial<Movie>) => {
    loading.value = true
    error.value = null

    try {
      const response = await moviesService.update(id, movieData)
      const index = movies.value.findIndex(movie => movie.id === id)
      if (index !== -1) {
        movies.value[index] = response
      }
      currentMovie.value = response
      return response
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

 const deleteMovie = async (id: string | number) => {
    loading.value = true
    error.value = null

    try {
      const response = await moviesService.delete(id)
      movies.value = movies.value.filter(movie => movie.id !== id)
      if (currentMovie.value?.id === id) {
        currentMovie.value = null
      }
      return response
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

 const incrementMovieViews = async (id: string | number) => {
    try {
      const response = await moviesService.incrementViews(id)
      // Обновляем локально количество просмотров
      const movie = movies.value.find(movie => movie.id === id)
      if (movie) {
        movie.views = response.views
      }
      if (currentMovie.value?.id === id) {
        currentMovie.value.views = response.views
      }
      return response
    } catch (err) {
      error.value = err
      throw err
    }
  }

  return {
    movies,
    currentMovie,
    loading,
    error,
    fetchMovies,
    fetchMovieById,
    createMovie,
    updateMovie,
    deleteMovie,
    incrementMovieViews
  }
}

// Композаблы для специфических операций
export function useMoviesByYear(year: number) {
  const loading = ref(false)
  const error = ref<any>(null)
  const movies = ref<Movie[]>([])

  const fetchMoviesByYear = async (skip: number = 0, limit: number = 100) => {
    loading.value = true
    error.value = null

    try {
      const response = await moviesService.getByYear(year, skip, limit)
      movies.value = response
      return response
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    movies,
    loading,
    error,
    fetchMoviesByYear
  }
}

export function useMoviesByGenre(genre: string) {
  const loading = ref(false)
  const error = ref<any>(null)
  const movies = ref<Movie[]>([])

  const fetchMoviesByGenre = async (skip: number = 0, limit: number = 100) => {
    loading.value = true
    error.value = null

    try {
      const response = await moviesService.getByGenre(genre, skip, limit)
      movies.value = response
      return response
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    movies,
    loading,
    error,
    fetchMoviesByGenre
  }
}