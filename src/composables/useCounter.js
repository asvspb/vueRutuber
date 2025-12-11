import { ref, computed } from 'vue'
import { useLocalStorage } from '@vueuse/core'

export function useCounter(initialValue = 0) {
  const count = useLocalStorage('counter', initialValue)

  const doubleCount = computed(() => count.value * 2)

  function increment() {
    count.value++
  }

  function decrement() {
    count.value--
  }

  function reset() {
    count.value = initialValue
  }

  return {
    count,
    doubleCount,
    increment,
    decrement,
    reset
  }
}