<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-xl font-bold pixel-font text-amber-900">成长日志</h1>
      <button @click="openForm" class="pixel-btn btn-grass px-3 py-2 rounded-lg text-sm">
        + 记录
      </button>
    </div>

    <div class="pixel-card rounded-xl p-4">
      <!-- 时间线 -->
      <div class="relative">
        <!-- 竖线 -->
        <div class="absolute left-[15px] top-2 bottom-2 w-0.5 bg-amber-200"></div>

        <div v-for="l in logs" :key="l.id" class="relative pl-10 pb-4 last:pb-0">
          <!-- 时间线圆点 -->
          <div
            class="absolute left-0 top-1 w-8 h-8 rounded-full flex items-center justify-center border-2"
            :class="l.score_delta != null ? (l.score_delta > 0 ? 'bg-green-100 border-green-400' : 'bg-red-100 border-red-400') : 'bg-amber-100 border-amber-400'"
          >
            <PixelIcon v-if="l.score_delta != null" type="gem" :size="16" />
            <PixelIcon v-else type="badge" :size="16" />
          </div>

          <!-- 内容卡片 -->
          <div class="rounded-lg p-3" :class="l.score_delta != null ? 'bg-amber-50' : 'bg-amber-50/50'">
            <div class="flex justify-between items-center">
              <div class="font-medium text-amber-900 text-sm">{{ l.title }}</div>
              <div class="text-xs text-amber-500">{{ formatTime(l.created_at) }}</div>
            </div>
            <p v-if="l.content" class="text-sm text-amber-700 mt-1">{{ l.content }}</p>
            <!-- 关联积分记录 -->
            <div v-if="l.score_delta != null" class="mt-2 flex items-center gap-2">
              <span
                class="px-2 py-0.5 rounded-full text-xs font-bold"
                :class="l.score_delta > 0 ? 'bg-green-200 text-green-700' : 'bg-red-200 text-red-700'"
              >
                {{ l.score_delta > 0 ? '+' : '' }}{{ l.score_delta }} 宝石
              </span>
              <span class="text-xs text-amber-600">{{ l.score_reason }}</span>
            </div>
            <button @click="removeLog(l)" class="text-red-400 text-xs mt-1 hover:text-red-600">删除</button>
          </div>
        </div>
      </div>
      <div v-if="!logs.length" class="text-center text-amber-500 py-6">暂无成长记录</div>
    </div>

    <div v-if="showForm" class="fixed inset-0 flex items-center justify-center p-4 z-20" @click.self="showForm = false">
      <div class="overlay-bg"></div>
      <div class="pixel-card rounded-xl p-5 relative max-w-sm w-full" @click.stop>
        <h2 class="font-bold mb-4 text-amber-900">记录成长瞬间</h2>
        <label class="block text-sm mb-1 text-amber-800">标题</label>
        <input v-model="form.title" class="w-full p-2 mb-3 rounded-lg border-2 border-amber-300 bg-white text-amber-900 outline-none focus:border-teal-400" />
        <label class="block text-sm mb-1 text-amber-800">内容</label>
        <textarea v-model="form.content" rows="3" class="w-full p-2 mb-4 rounded-lg border-2 border-amber-300 bg-white text-amber-900 outline-none focus:border-teal-400"></textarea>
        <div class="flex gap-3">
          <button @click="showForm = false" class="flex-1 pixel-btn py-2 rounded-lg btn-wood">取消</button>
          <button @click="save" class="flex-1 pixel-btn py-2 rounded-lg btn-grass">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { api } from '@/api'
import { playSound } from '@/utils/sound'
import PixelIcon from '@/components/game/PixelIcon.vue'

const logs = ref<any[]>([])
const showForm = ref(false)
const form = reactive({ title: '', content: '' })

function formatTime(t: any) {
  if (!t) return ''
  const d = new Date(t)
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const mins = String(d.getMinutes()).padStart(2, '0')
  return `${month}-${day} ${hours}:${mins}`
}

async function load() {
  logs.value = await api.getLogs(100)
}

function openForm() {
  playSound('click')
  Object.assign(form, { title: '', content: '' })
  showForm.value = true
}

async function save() {
  if (!form.title) return
  await api.createLog({ ...form })
  showForm.value = false
  await load()
}

async function removeLog(l: any) {
  if (confirm('删除这条记录？')) {
    await api.deleteLog(l.id)
    await load()
  }
}

onMounted(load)
</script>

<style scoped>
.overlay-bg {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
}
</style>
