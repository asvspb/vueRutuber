import { createRouter, createWebHistory } from 'vue-router'
import PlaylistsChannelsView from '../components/PlaylistsChannelsView.vue'

const routes = [
  {
    path: '/playlists/:playlistId?',
    name: 'Playlists',
    component: PlaylistsChannelsView,
    props: true
  },
  {
    path: '/',
    redirect: '/playlists'
  }
] as const

const router = createRouter({
  history: createWebHistory(),
  routes: routes as any
})

export default router