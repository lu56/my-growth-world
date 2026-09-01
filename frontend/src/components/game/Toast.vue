<template>
  <Teleport to="body">
    <div class="toast-container">
      <TransitionGroup name="toast">
        <div
          v-for="t in toastStore.toasts"
          :key="t.id"
          class="toast-item pixel-card"
          :class="toastClass(t.type)"
          @click="toastStore.remove(t.id)"
        >
          <span class="toast-icon">{{ iconFor(t.type) }}</span>
          <span class="toast-msg">{{ t.message }}</span>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { useToastStore } from '@/stores/toast'
import type { ToastItem } from '@/stores/toast'

const toastStore = useToastStore()

function toastClass(type: ToastItem['type']): string {
  switch (type) {
    case 'success': return 'toast-success'
    case 'error': return 'toast-error'
    default: return 'toast-info'
  }
}

function iconFor(type: ToastItem['type']): string {
  switch (type) {
    case 'success': return '\u2713'
    case 'error': return '\u2717'
    default: return '\u2139'
  }
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  pointer-events: none;
  width: 90%;
  max-width: 360px;
}

.toast-item {
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  cursor: pointer;
  width: 100%;
  box-sizing: border-box;
}

.toast-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.toast-success {
  background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
  border: 2px solid #43a047;
  color: #1b5e20;
}

.toast-error {
  background: linear-gradient(135deg, #ffcdd2, #ef9a9a);
  border: 2px solid #e53935;
  color: #b71c1c;
}

.toast-info {
  background: linear-gradient(135deg, #bbdefb, #90caf9);
  border: 2px solid #1e88e5;
  color: #0d47a1;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100px);
}
</style>
