<template>
  <v-app>
    <v-app-bar color="primary" dark>
      <v-app-bar-nav-icon></v-app-bar-nav-icon>
      <v-app-bar-title>
        <span class="text-h6">🎬 Rutube Playlist Manager</span>
      </v-app-bar-title>
      <template v-slot:append>
        <v-btn icon="mdi-magnify"></v-btn>
        <v-btn icon="mdi-dots-vertical"></v-btn>
      </template>
    </v-app-bar>

    <v-main>
      <PlaylistsChannelsView />
    </v-main>

    <v-footer app>
      <span>&copy; {{ new Date().getFullYear() }} Rutube Playlist Manager</span>
    </v-footer>
  </v-app>
</template>

<script setup lang="ts">
import PlaylistsChannelsView from './components/PlaylistsChannelsView.vue'
</script>

<style lang="scss">
  @use './styles/variables.scss' as *;
  @use './styles/mixins.scss' as *;

  #app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: $primary-text-color;
  }

  .v-application {
    background-color: #f5f5f5 !important;
  }
</style>