import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface ToastItem {
  id: number
  message: string
  type: 'success' | 'error' | 'info'
}

let toastId = 0

export const useToastStore = defineStore('toast', () => {
  const toasts = ref<ToastItem[]>([])

  function show(message: string, type: ToastItem['type'] = 'info', duration = 2500) {
    const id = ++toastId
    toasts.value.push({ id, message, type })
    setTimeout(() => {
      remove(id)
    }, duration)
  }

  function success(message: string) {
    show(message, 'success')
  }

  function error(message: string) {
    show(message, 'error', 3500)
  }

  function info(message: string) {
    show(message, 'info')
  }

  function remove(id: number) {
    const idx = toasts.value.findIndex((t) => t.id === id)
    if (idx >= 0) toasts.value.splice(idx, 1)
  }

  return { toasts, show, success, error, info, remove }
})
