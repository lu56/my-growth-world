<template>
  <div class="pixel-card rounded-xl p-4 mb-4 anim-slide-up">
    <div class="flex items-center gap-4">
      <!-- 像素角色头像 -->
      <div class="avatar-frame anim-float">
        <PixelIcon type="avatar" :level="level?.level || 1" :size="56" />
      </div>
      <div class="flex-1">
        <div class="text-lg font-bold pixel-font text-amber-900">{{ child?.name || '小勇士' }}</div>
        <div class="text-orange-700 text-sm font-semibold">Lv.{{ level?.level }} · {{ level?.level_name }}</div>
        <div class="flex items-center gap-1 mt-1 text-sm">
          <PixelIcon type="gem" :size="18" />
          <span class="font-bold text-base text-teal-700">{{ balance }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'
import PixelIcon from './PixelIcon.vue'

const store = useAppStore()
const child = computed(() => store.child)
const balance = computed(() => store.balance)
const level = computed(() => store.level)
</script>

<style scoped>
.avatar-frame {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid #ffb300;
  border-radius: 12px;
  background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
  box-shadow: 0 3px 0 #e65100;
}
</style>
