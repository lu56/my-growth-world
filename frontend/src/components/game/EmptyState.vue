<template>
  <div class="empty-state">
    <div class="empty-icon">{{ icon }}</div>
    <div class="empty-text">{{ text }}</div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  text?: string
  icon?: string
}>(), {
  text: '暂无数据',
  icon: '\uD83D\uDD0E',
})
</script>

<style scoped>
.empty-state {
  text-align: center;
  padding: 32px 16px;
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 8px;
  opacity: 0.5;
}

.empty-text {
  font-size: 14px;
  color: #9e9e9e;
  font-weight: 500;
}
</style>
