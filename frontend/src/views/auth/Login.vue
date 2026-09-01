<template>
  <div class="min-h-screen flex flex-col items-center justify-center p-6 login-bg">
    <div class="text-center mb-6">
      <PixelIcon type="avatar" :level="1" :size="56" class="mb-2" />
      <h1 class="text-3xl font-bold pixel-font text-white">我的成长世界</h1>
      <p class="text-white/70 mt-1">{{ mode === 'child' ? '小朋友登录 · 进入成长世界' : '家长登录 · 进入管理' }}</p>
    </div>

    <div class="w-full max-w-sm login-card p-6 rounded-2xl">
      <!-- Tab 切换 -->
      <div class="flex gap-2 mb-4">
        <button
          @click="mode = 'child'"
          class="flex-1 py-2 rounded-lg text-sm font-bold transition-colors"
          :class="mode === 'child' ? 'bg-teal-600 text-white' : 'bg-amber-100 text-amber-700'"
        >我是小朋友</button>
        <button
          @click="mode = 'parent'"
          class="flex-1 py-2 rounded-lg text-sm font-bold transition-colors"
          :class="mode === 'parent' ? 'bg-amber-600 text-white' : 'bg-amber-100 text-amber-700'"
        >我是家长</button>
      </div>

      <form @submit.prevent="doLogin">
        <label class="block text-sm mb-2 text-amber-800">
          {{ mode === 'child' ? '小朋友口令' : '家长口令' }}
        </label>
        <input
          v-model="password"
          type="password"
          class="w-full p-3 rounded-lg border-2 border-amber-300 bg-white text-amber-900 outline-none focus:border-teal-400"
          :placeholder="mode === 'child' ? '请输入小朋友口令' : '请输入家长口令'"
        />
        <button
          type="submit"
          class="w-full mt-4 pixel-btn btn-gem py-3 rounded-lg font-bold text-lg"
          :disabled="loading"
        >
          {{ loading ? '进入中...' : '进入世界' }}
        </button>
        <p v-if="error" class="text-red-500 text-sm mt-3 text-center bg-red-50 px-3 py-1 rounded-lg">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { playSound } from '@/utils/sound'
import PixelIcon from '@/components/game/PixelIcon.vue'

const route = useRoute()
const router = useRouter()
const store = useAppStore()
const mode = ref<'child' | 'parent'>(
  (route.query.mode as 'child' | 'parent') === 'child' ? 'child' : 'parent'
)
const password = ref('')
const loading = ref(false)
const error = ref('')

watch(
  () => route.query.mode,
  (m) => {
    if (m === 'child' || m === 'parent') mode.value = m
  }
)

async function doLogin() {
  if (!password.value) {
    error.value = '请输入口令'
    return
  }
  loading.value = true
  error.value = ''
  try {
    if (mode.value === 'child') {
      await store.childLogin(password.value)
      playSound('click')
      router.push('/home')
    } else {
      await store.login(password.value)
      playSound('click')
      router.push('/parent/dashboard')
    }
  } catch (e: any) {
    error.value = e.message || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-bg {
  background:
    radial-gradient(circle at 20% 20%, rgba(124, 179, 66, 0.3), transparent 40%),
    radial-gradient(circle at 80% 30%, rgba(79, 195, 247, 0.2), transparent 40%),
    linear-gradient(180deg, #1b5e20 0%, #2e7d32 50%, #388e3c 100%);
}

.login-card {
  background: linear-gradient(135deg, #fff8e1 0%, #fff3cd 100%);
  border: 4px solid #ffb300;
  box-shadow: 0 6px 0 #e65100, 0 10px 20px rgba(0,0,0,0.3);
}
</style>
