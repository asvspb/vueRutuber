import { ref } from 'vue'

export function useNotify() {
  const notifications = ref([])

  function show(message, type = 'info', duration = 3000) {
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

  function success(message, duration = 3000) {
    return show(message, 'success', duration)
  }

  function error(message, duration = 5000) {
    return show(message, 'error', duration)
  }

  function warning(message, duration = 4000) {
    return show(message, 'warning', duration)
  }

  function info(message, duration = 3000) {
    return show(message, 'info', duration)
  }

  function remove(id) {
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