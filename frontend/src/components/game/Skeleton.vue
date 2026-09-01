<template>
  <div class="skeleton-wrapper">
    <div
      v-for="n in count"
      :key="n"
      class="skeleton-item"
      :style="{ height: height + 'px', borderRadius: radius + 'px' }"
    ></div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  count?: number
  height?: number
  radius?: number
}>(), {
  count: 1,
  height: 48,
  radius: 10,
})
</script>

<style scoped>
.skeleton-wrapper {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skeleton-item {
  width: 100%;
  background: linear-gradient(90deg, #e0e0e0 25%, #f5f5f5 50%, #e0e0e0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
</style>
