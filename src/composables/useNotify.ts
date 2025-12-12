import { ref } from 'vue'

interface Notification {
  id: number
  message: string
  type: string
  duration: number
}

export function useNotify() {
  const notifications = ref<Notification[]>([])

  function show(message: string, type = 'info', duration = 3000) {
    const id = Date.now()
    const notification = {
      id,
      message,
      type,
      duration
    }

    notifications.value.push(notification)

    // Автоматическое удаление
    setTimeout(() => {
      remove(id)
    }, duration)

    return id
  }

  function success(message: string, duration = 3000) {
    return show(message, 'success', duration)
  }

  function error(message: string, duration = 5000) {
    return show(message, 'error', duration)
  }

  function warning(message: string, duration = 4000) {
    return show(message, 'warning', duration)
  }

  function info(message: string, duration = 3000) {
    return show(message, 'info', duration)
  }

  function remove(id: number) {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  function clear() {
    notifications.value = []
  }

  return {
    notifications,
    show,
    success,
    error,
    warning,
    info,
    remove,
    clear
  }
}