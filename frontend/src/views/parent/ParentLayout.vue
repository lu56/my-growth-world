<template>
  <div class="min-h-screen parent-bg">
    <!-- 顶栏 -->
    <header class="sticky top-0 z-10 bg-grass-700 border-b-4 border-grass-800 px-4 py-3 flex items-center justify-between shadow-lg">
      <router-link to="/parent/dashboard" class="flex items-center gap-2">
        <PixelIcon type="avatar" :level="store.level?.level || 1" :size="28" />
        <span class="font-bold pixel-font text-white">我的成长世界</span>
      </router-link>
      <div class="flex items-center gap-2">
        <div class="flex items-center gap-1 bg-grass-600 px-3 py-1 rounded-full">
          <PixelIcon type="gem" :size="16" />
          <span class="text-white font-bold text-sm">{{ store.balance }}</span>
        </div>
        <button @click="logout" class="pixel-btn btn-red text-white text-xs px-3 py-1 rounded-lg">退出</button>
      </div>
    </header>

    <div class="max-w-3xl mx-auto p-4 pb-24">
      <router-view />
    </div>

    <!-- 底部导航 -->
    <nav class="fixed bottom-0 left-0 right-0 bg-grass-800 border-t-4 border-grass-900 z-10">
      <div class="max-w-3xl mx-auto grid grid-cols-8 gap-1 p-2">
        <router-link
          v-for="item in navs"
          :key="item.to"
          :to="item.to"
          class="flex flex-col items-center py-2 rounded-lg text-xs transition-colors"
          :class="isActive(item.to) ? 'bg-grass-500 text-white' : 'text-grass-200'"
        >
          <PixelIcon :type="item.iconType" :task-type="item.iconTask" :reward-key="item.iconReward" :code="item.iconCode" :size="24" />
          <span class="mt-1">{{ item.label }}</span>
        </router-link>
      </div>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { playSound } from '@/utils/sound'
import PixelIcon from '@/components/game/PixelIcon.vue'

const store = useAppStore()
const router = useRouter()
const route = useRoute()

const navs = [
  { to: '/parent/dashboard', label: '看板', iconType: 'gem' as const, iconTask: '', iconReward: '', iconCode: '' },
  { to: '/parent/scores', label: '积分', iconType: 'badge' as const, iconTask: '', iconReward: '', iconCode: 'score' },
  { to: '/parent/rules', label: '规则', iconType: 'task' as const, iconTask: '学习', iconReward: '', iconCode: '' },
  { to: '/parent/rewards', label: '商城', iconType: 'reward' as const, iconTask: '', iconReward: 'gift', iconCode: '' },
  { to: '/parent/tickets', label: '奖券', iconType: 'badge' as const, iconTask: '', iconReward: '', iconCode: 'challenge' },
  { to: '/parent/shop', label: '商店', iconType: 'reward' as const, iconTask: '', iconReward: 'snack', iconCode: '' },
  { to: '/parent/logs', label: '日志', iconType: 'badge' as const, iconTask: '', iconReward: '', iconCode: 'checkin' },
  { to: '/parent/settings', label: '设置', iconType: 'badge' as const, iconTask: '', iconReward: '', iconCode: 'goal' },
]

function isActive(to: string) {
  return route.path === to
}

function logout() {
  playSound('click')
  store.logout()
  router.push('/home')
}

// 点击导航时播放点击音效
</script>

<style scoped>
.parent-bg {
  background: linear-gradient(180deg, #e8f5e9 0%, #c8e6c9 100%);
}
</style>
