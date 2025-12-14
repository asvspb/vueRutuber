# src/services

Сервисы для взаимодействия с Backend API.

## Файлы

| Файл | Описание |
|------|----------|
| `api.ts` | Axios instance с `VITE_API_BASE_URL` |
| `moviesService.ts` | API методы для работы с фильмами |

## api.ts

```typescript
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api'
})

export default api
```

## moviesService.ts

```typescript
// Методы
getMovies(skip?: number, limit?: number): Promise<Movie[]>
getMovieById(id: number): Promise<Movie>
createMovie(movie: MovieCreate): Promise<Movie>
updateMovie(id: number, movie: MovieUpdate): Promise<Movie>
deleteMovie(id: number): Promise<void>
```