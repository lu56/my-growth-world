<template>
  <div>
    <h1 class="text-xl font-bold text-grass-100 mb-4 flex items-center gap-2">
      <span class="text-2xl">⚔️</span> 挑战商店
    </h1>

    <!-- 创建新任务 -->
    <div class="pixel-card rounded-xl p-4 mb-4">
      <h2 class="font-bold text-amber-900 mb-3 text-sm">发布新挑战</h2>
      <div class="space-y-2">
        <input
          v-model="form.title"
          placeholder="挑战标题（如：独立完成数学作业）"
          class="w-full p-2 rounded-lg border-2 border-amber-300 bg-white text-amber-900 text-sm outline-none focus:border-teal-400"
        />
        <input
          v-model="form.description"
          placeholder="挑战说明（可选）"
          class="w-full p-2 rounded-lg border-2 border-amber-300 bg-white text-amber-900 text-sm outline-none focus:border-teal-400"
        />
        <div class="flex gap-2">
          <div class="flex items-center gap-1 flex-1">
            <PixelIcon type="gem" :size="16" />
            <input
              v-model.number="form.reward"
              type="number"
              min="1"
              class="w-20 p-2 rounded-lg border-2 border-amber-300 bg-white text-amber-900 text-sm outline-none focus:border-teal-400"
            />
            <span class="text-xs text-amber-600">宝石奖励</span>
          </div>
          <button
            @click="createTask"
            :disabled="!form.title || form.reward <= 0"
            class="pixel-btn btn-grass px-4 py-2 rounded-lg text-sm disabled:opacity-50"
          >发布</button>
        </div>
      </div>
    </div>

    <!-- 待确认任务 -->
    <div v-if="pendingTasks.length" class="mb-4">
      <div class="text-sm font-bold text-orange-700 mb-2 flex items-center gap-1">
        <span class="animate-pulse">🔔</span> 待确认 ({{ pendingTasks.length }})
      </div>
      <div
        v-for="t in pendingTasks"
        :key="t.id"
        class="pixel-card rounded-xl p-3 mb-2 border-2 border-orange-400"
      >
        <div class="flex items-center justify-between">
          <div>
            <div class="font-bold text-sm text-amber-900">{{ t.title }}</div>
            <div v-if="t.description" class="text-[10px] text-amber-600">{{ t.description }}</div>
            <div class="flex items-center gap-2 mt-1">
              <span class="text-xs flex items-center gap-1 text-teal-600 font-bold">
                <PixelIcon type="gem" :size="12" />{{ t.reward }}
              </span>
              <span class="text-[10px] text-amber-500">提交于 {{ t.completed_at || '未知' }}</span>
            </div>
          </div>
          <div class="flex gap-1">
            <button
              @click="confirmTask(t)"
              :disabled="loading"
              class="pixel-btn btn-grass px-3 py-2 rounded-lg text-xs"
            >确认发奖</button>
            <button
              @click="rejectTask(t)"
              :disabled="loading"
              class="pixel-btn btn-red px-3 py-2 rounded-lg text-xs"
            >驳回</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 所有任务列表 -->
    <div class="pixel-card rounded-xl p-4">
      <div class="flex justify-between items-center mb-3">
        <h2 class="font-bold text-amber-900 text-sm">全部挑战</h2>
        <span class="text-xs bg-amber-200 px-2 py-1 rounded-full text-amber-700 font-bold">{{ tasks.length }} 个</span>
      </div>
      <Skeleton v-if="loading" :count="3" :height="60" />
      <div v-else-if="tasks.length" class="space-y-2">
        <div
          v-for="t in tasks"
          :key="t.id"
          class="rounded-lg p-3 border-2"
          :class="taskBorderClass(t.status)"
        >
          <div class="flex items-center justify-between">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span class="font-bold text-sm text-amber-900 truncate">{{ t.title }}</span>
                <span class="text-[9px] px-2 py-0.5 rounded-full font-bold flex-shrink-0" :class="statusClass(t.status)">
                  {{ statusLabel(t.status) }}
                </span>
              </div>
              <div v-if="t.description" class="text-[10px] text-amber-600 mt-0.5 truncate">{{ t.description }}</div>
              <div class="flex items-center gap-3 mt-1 text-[10px] text-amber-500">
                <span class="flex items-center gap-1">
                  <PixelIcon type="gem" :size="10" />{{ t.reward }}
                </span>
                <span v-if="t.accepted_at">接取 {{ t.accepted_at }}</span>
                <span v-if="t.completed_at">完成 {{ t.completed_at }}</span>
              </div>
            </div>
            <!-- 删除按钮：仅 available 或 completed 状态 -->
            <button
              v-if="t.status === 'available' || t.status === 'completed'"
              @click="deleteTask(t)"
              :disabled="loading"
              class="pixel-btn btn-red px-2 py-1.5 rounded-lg text-[10px] ml-2 flex-shrink-0"
            >删除</button>
          </div>
        </div>
      </div>
      <EmptyState v-else icon="🗺️" text="还没有发布任何挑战" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import PixelIcon from '@/components/game/PixelIcon.vue'
import Skeleton from '@/components/game/Skeleton.vue'
import EmptyState from '@/components/game/EmptyState.vue'
import { api } from '@/api'
import { useAppStore } from '@/stores/app'
import { useEffectStore } from '@/stores/effect'
import { useToastStore } from '@/stores/toast'
import { playSound } from '@/utils/sound'

const store = useAppStore()
const effectStore = useEffectStore()
const toast = useToastStore()

const tasks = ref<any[]>([])
const loading = ref(false)
const form = ref({ title: '', description: '', reward: 10 })

const pendingTasks = computed(() => tasks.value.filter((t) => t.status === 'pending_review'))

function statusLabel(status: string): string {
  const map: Record<string, string> = {
    available: '可接取',
    accepted: '进行中',
    pending_review: '待确认',
    completed: '已完成',
  }
  return map[status] || status
}

function statusClass(status: string): string {
  const map: Record<string, string> = {
    available: 'bg-blue-100 text-blue-600',
    accepted: 'bg-teal-100 text-teal-600',
    pending_review: 'bg-orange-100 text-orange-600',
    completed: 'bg-green-100 text-green-600',
  }
  return map[status] || ''
}

function taskBorderClass(status: string): string {
  const map: Record<string, string> = {
    available: 'border-blue-300 bg-blue-50',
    accepted: 'border-teal-300 bg-teal-50',
    pending_review: 'border-orange-300 bg-orange-50',
    completed: 'border-green-300 bg-green-50',
  }
  return map[status] || 'border-amber-300'
}

async function loadTasks() {
  loading.value = true
  try {
    tasks.value = await api.getShopTasks()
  } catch (e: any) {
    toast.error(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

async function createTask() {
  if (!form.value.title || form.value.reward <= 0) return
  try {
    await api.createShopTask({
      title: form.value.title,
      description: form.value.description,
      reward: form.value.reward,
    })
    form.value = { title: '', description: '', reward: 10 }
    playSound('click')
    toast.success('挑战已发布！')
    await loadTasks()
  } catch (e: any) {
    toast.error(e.message || '创建失败')
  }
}

async function confirmTask(t: any) {
  loading.value = true
  try {
    const res = await api.confirmShopTask(t.id)
    playSound('levelup')
    toast.success(`已确认「${t.title}」，奖励 ${t.reward} 宝石！`)
    await store.refreshBalance()
    effectStore.handleApiResponse(res)
    await loadTasks()
  } catch (e: any) {
    toast.error(e.message || '确认失败')
  } finally {
    loading.value = false
  }
}

async function rejectTask(t: any) {
  loading.value = true
  try {
    await api.rejectShopTask(t.id)
    toast.info(`已驳回「${t.title}」`)
    await loadTasks()
  } catch (e: any) {
    toast.error(e.message || '驳回失败')
  } finally {
    loading.value = false
  }
}

async function deleteTask(t: any) {
  if (!confirm(`确定删除「${t.title}」？`)) return
  try {
    await api.deleteShopTask(t.id)
    toast.success('已删除')
    await loadTasks()
  } catch (e: any) {
    toast.error(e.message || '删除失败')
  }
}

onMounted(loadTasks)
</script>
