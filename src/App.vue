<template>
  <div id="app">
    <header>
      <h1>VueExpert Frontend</h1>
    </header>

    <main>

      <!-- Добавляем компонент MovieList -->
      <section class="movies-section">
        <div class="movies-container">
          <h2 class="movies-title">Фильмы</h2>
          <MovieList @movie-selected="handleMovieSelected" />
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import MovieList from './components/MovieList.vue'



// Обработчик события выбора фильма
const handleMovieSelected = (movie) => {
  selectedMovie.value = movie
  console.log('Выбран фильм:', movie)
};
</script>

<style lang="scss">
  @use './styles/variables.scss' as *;
  @use './styles/mixins.scss' as *;

 #app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: $primary-text-color;
    margin-top: 60px;
    padding: 0 20px;
  }
  
  header {
    margin-bottom: 30px;
  }
  
  h1 {
    color: $primary-text-color;
    margin-bottom: 20px;
  }
  
  main {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  
  .movies-section {
    width: 100%;
    margin-top: 40px;
  }
  
  .movies-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
  }
  
  .movies-title {
    color: $primary-text-color;
    margin-bottom: 20px;
    font-size: 2rem;
  }
  
  .inner-container {
    @include flex-center;
    gap: 10px;
  }
  
  .example {
    &__container {
      @include container(800px);
      @include shadow(2);
      margin: 20px auto;
      padding: $padding-medium;
      border: 1px solid $border-color;
      border-radius: $border-radius;
      background-color: $background-color;
    }

    &__title {
      margin-bottom: 10px;
    }

    &__text {
      font-size: $font-size-large;
      color: $accent-color;
      margin: 15px 0;
      @include responsive-font($font-size-medium, $font-size-large);
    }

    &__nested {
      padding: $padding-medium;
      background-color: $secondary-background;
      border-radius: $border-radius;
      margin-top: $padding-medium;

      &-text {
        margin: 10px 0;
        font-weight: bold;
      }
    }

    &__button {
      padding: 10px 20px;
      font-size: $font-size-medium;
    }

    &__button--secondary {
      @include button-style($button-secondary-bg);
    }
  }

  h1 {
    @include responsive-font($font-size-large, $font-size-xlarge);
    @include gradient(#f8f9fa, #e9ecef);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 20px;
    padding: 10px;
  }
</style>