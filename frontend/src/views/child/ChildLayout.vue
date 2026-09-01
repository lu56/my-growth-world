<template>
  <div class="min-h-screen child-bg pb-20">
    <!-- 顶部余额条（非首页时显示） -->
    <div v-if="!isHome" class="sticky top-0 z-10 bg-amber-700/90 backdrop-blur px-4 py-2 flex items-center justify-between shadow-md">
      <div class="flex items-center gap-2">
        <PixelIcon type="avatar" :level="store.level?.level || 1" :size="24" />
        <span class="font-bold text-white text-sm pixel-font">{{ store.child?.name || '小勇士' }}</span>
      </div>
      <div class="flex items-center gap-2">
        <div class="flex items-center gap-1 bg-amber-600 px-3 py-1 rounded-full">
          <PixelIcon type="gem" :size="16" />
          <span class="text-white font-bold text-sm">{{ store.balance }}</span>
        </div>
        <button
          @click="logout"
          class="bg-amber-800/90 hover:bg-amber-900 text-white text-xs font-bold px-3 py-1.5 rounded-full transition-colors"
        >
          退出
        </button>
      </div>
    </div>

    <!-- 首页悬浮退出按钮 -->
    <button
      v-if="isHome"
      @click="logout"
      class="fixed top-3 right-3 z-20 bg-white/90 text-amber-800 text-xs font-bold px-3 py-1.5 rounded-full border-2 border-amber-300 shadow-md hover:bg-white transition-colors"
    >
      退出
    </button>

    <div class="max-w-md mx-auto p-4">
      <router-view />
    </div>

    <!-- 底部 Tab 导航 -->
    <nav class="fixed bottom-0 left-0 right-0 z-20 child-nav-border">
      <div class="max-w-md mx-auto grid grid-cols-4 gap-1 p-2">
        <router-link
          v-for="item in tabs"
          :key="item.to"
          :to="item.to"
          class="flex flex-col items-center py-2 rounded-xl transition-all"
          :class="isActive(item.to) ? 'tab-active' : 'tab-inactive'"
        >
          <span class="text-2xl leading-none">{{ isActive(item.to) ? item.iconActive : item.icon }}</span>
          <span class="mt-1 text-[11px] font-bold">{{ item.label }}</span>
        </router-link>
      </div>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import PixelIcon from '@/components/game/PixelIcon.vue'

const store = useAppStore()
const route = useRoute()
const router = useRouter()

const tabs = [
  { to: '/home', label: '首页', icon: '🏠', iconActive: '🏠' },
  { to: '/challenge', label: '挑战', icon: '🗺️', iconActive: '⚔️' },
  { to: '/rewards', label: '宝箱', icon: '📦', iconActive: '🎁' },
  { to: '/achievements', label: '成就', icon: '🏅', iconActive: '🏆' },
]

const isHome = computed(() => route.path === '/home')
function isActive(to: string) {
  return route.path === to
}

function logout() {
  store.logout()
  router.replace({ name: 'login', query: { mode: 'child' } })
}

onMounted(() => {
  if (!store.child) {
    store.loadCore()
  }
})
</script>

<style scoped>
.child-bg {
  background:
    radial-gradient(circle at 20% 20%, rgba(124, 179, 66, 0.25), transparent 40%),
    radial-gradient(circle at 80% 30%, rgba(79, 195, 247, 0.2), transparent 40%),
    radial-gradient(circle at 50% 80%, rgba(255, 213, 79, 0.15), transparent 40%),
    linear-gradient(180deg, #e8f5e9 0%, #c8e6c9 50%, #a5d6a7 100%);
}

.child-nav-border {
  background: linear-gradient(180deg, #fff8e1, #fff3cd);
  border-top: 4px solid #3e2723;
  box-shadow: 0 -4px 12px rgba(0,0,0,0.1);
}

.tab-active {
  background: linear-gradient(180deg, #66bb6a, #43a047);
  color: #fff;
  box-shadow: 0 3px 0 #2e7d32;
}

.tab-inactive {
  color: #8d6e63;
}
</style>
