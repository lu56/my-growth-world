<template>
  <div>
    <!-- 亲子任务商店 -->
    <div class="pixel-card rounded-xl p-4 mb-4">
      <div class="flex justify-between items-center mb-3">
        <h2 class="font-bold text-amber-900 text-lg flex items-center gap-2">
          <span class="text-2xl">⚔️</span> 挑战商店
        </h2>
      </div>
      <Skeleton v-if="loading" :count="2" :height="60" />
      <template v-else>
        <!-- 可接受的任务 -->
        <div v-if="availableShopTasks.length" class="mb-3">
          <div class="text-[10px] text-orange-600 font-bold mb-1">可接取的挑战</div>
          <div
            v-for="t in availableShopTasks"
            :key="t.id"
            class="shop-card rounded-lg p-3 mb-2 flex items-center justify-between"
          >
            <div class="flex-1">
              <div class="font-bold text-sm text-amber-900">{{ t.title }}</div>
              <div v-if="t.description" class="text-[10px] text-amber-600">{{ t.description }}</div>
            </div>
            <div class="flex items-center gap-2">
              <div class="flex items-center gap-1 text-teal-600 font-bold text-sm">
                <PixelIcon type="gem" :size="14" />{{ t.reward }}
              </div>
              <button
                @click="acceptShopTask(t)"
                :disabled="shopLoading"
                class="pixel-btn btn-grass px-3 py-1.5 rounded-lg text-xs"
              >接受</button>
            </div>
          </div>
        </div>
        <!-- 我的任务 -->
        <div v-if="myShopTasks.length">
          <div class="text-[10px] text-purple-600 font-bold mb-1">我的挑战</div>
          <div
            v-for="t in myShopTasks"
            :key="t.id"
            class="shop-card rounded-lg p-3 mb-2"
            :class="taskStatusBg(t.status)"
          >
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <div class="font-bold text-sm text-amber-900">{{ t.title }}</div>
                <div class="flex items-center gap-2 mt-0.5">
                  <span class="text-[10px] flex items-center gap-1 text-teal-600">
                    <PixelIcon type="gem" :size="12" />{{ t.reward }}
                  </span>
                  <span class="text-[9px] px-2 py-0.5 rounded-full font-bold" :class="shopStatusLabelClass(t.status)">
                    {{ shopStatusLabel(t.status) }}
                  </span>
                </div>
              </div>
              <div class="flex gap-1">
                <button
                  v-if="t.status === 'accepted'"
                  @click="submitShopTask(t)"
                  :disabled="shopLoading"
                  class="pixel-btn btn-grass px-2 py-1.5 rounded-lg text-[10px]"
                >提交</button>
                <button
                  v-if="t.status === 'accepted'"
                  @click="cancelShopTask(t)"
                  :disabled="shopLoading"
                  class="pixel-btn btn-wood px-2 py-1.5 rounded-lg text-[10px]"
                >取消</button>
                <span v-if="t.status === 'pending_review'" class="text-[10px] text-amber-600 self-center">等待确认...</span>
                <span v-if="t.status === 'completed'" class="text-lg self-center">✅</span>
              </div>
            </div>
          </div>
        </div>
        <EmptyState
          v-if="!availableShopTasks.length && !myShopTasks.length"
          icon="🗺️" text="暂无可接取的挑战"
        />
      </template>
    </div>

    <!-- 我的目标 -->
    <div class="pixel-card rounded-xl p-4 mb-4">
      <div class="flex justify-between items-center mb-3">
        <h2 class="font-bold text-amber-900 text-lg flex items-center gap-2">
          <PixelIcon type="badge" :size="24" /> 我的目标
        </h2>
        <button @click="showGoalForm = true" class="pixel-btn btn-grass px-2 py-1 rounded-lg text-xs">
          + 新目标
        </button>
      </div>
      <div v-if="goals.length" class="space-y-2">
        <div
          v-for="g in goals"
          :key="g.id"
          class="rounded-lg p-3 border-2"
          :class="goalCardClass(g)"
        >
          <div class="flex justify-between items-center">
            <div class="font-bold text-sm text-amber-900">{{ g.title }}</div>
            <span class="text-[10px] px-2 py-0.5 rounded-full font-bold" :class="goalStatusClass(g)">
              {{ goalStatusLabel(g) }}
            </span>
          </div>
          <p v-if="g.description" class="text-xs text-amber-600 mt-1">{{ g.description }}</p>
          <div v-if="g.status === 'approved' || g.status === 'completed'" class="mt-2">
            <div class="flex justify-between text-[10px] text-amber-700 mb-1">
              <span>{{ g.progress_score }} / {{ g.target_score }} 宝石</span>
              <span v-if="g.bonus_score">奖励 +{{ g.bonus_score }}</span>
            </div>
            <div class="h-2 bg-amber-200 rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-500"
                :style="{ width: `${(g.progress_ratio || 0) * 100}%`, background: g.status === 'completed' ? '#22c55e' : '#0d9488' }"
              ></div>
            </div>
          </div>
          <div v-if="g.deadline" class="text-[10px] text-amber-500 mt-1">截止 {{ g.deadline }}</div>
        </div>
      </div>
      <EmptyState v-else icon="🎯" text="还没有目标，设定一个小目标开始挑战吧！" />
    </div>

    <!-- 新建目标弹窗 -->
    <div v-if="showGoalForm" class="fixed inset-0 flex items-center justify-center p-4 z-30" @click.self="showGoalForm = false">
      <div class="overlay-bg"></div>
      <div class="pixel-card rounded-xl p-5 relative max-w-sm w-full" @click.stop>
        <h2 class="font-bold mb-4 text-amber-900">设定新目标</h2>
        <label class="block text-sm mb-1 text-amber-800">目标名称</label>
        <input v-model="goalForm.title" placeholder="如：累计100颗宝石" class="w-full p-2 mb-3 rounded-lg border-2 border-amber-300 bg-white text-amber-900 outline-none focus:border-teal-400" />
        <label class="block text-sm mb-1 text-amber-800">目标宝石数</label>
        <input v-model.number="goalForm.target_score" type="number" min="1" class="w-full p-2 mb-3 rounded-lg border-2 border-amber-300 bg-white text-amber-900 outline-none focus:border-teal-400" />
        <label class="block text-sm mb-1 text-amber-800">说明（可选）</label>
        <input v-model="goalForm.description" placeholder="想要什么奖励？" class="w-full p-2 mb-3 rounded-lg border-2 border-amber-300 bg-white text-amber-900 outline-none focus:border-teal-400" />
        <label class="block text-sm mb-1 text-amber-800">截止日期（可选）</label>
        <input v-model="goalForm.deadline" type="date" class="w-full p-2 mb-4 rounded-lg border-2 border-amber-300 bg-white text-amber-900" />
        <div class="text-xs text-amber-600 mb-3">
          达成后自动奖励目标宝石数的 10%（{{ Math.ceil((goalForm.target_score || 0) * 0.1) }} 颗）额外宝石！
        </div>
        <div class="flex gap-3">
          <button @click="showGoalForm = false" class="flex-1 pixel-btn py-2 rounded-lg btn-wood">取消</button>
          <button @click="createGoal" :disabled="!goalForm.title || !goalForm.target_score" class="flex-1 pixel-btn py-2 rounded-lg btn-grass disabled:opacity-50">提交</button>
        </div>
      </div>
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

const loading = ref(false)
const shopTasks = ref<any[]>([])
const goals = ref<any[]>([])
const shopLoading = ref(false)
const showGoalForm = ref(false)
const goalForm = ref({ title: '', target_score: 50, description: '', deadline: '' })

const availableShopTasks = computed(() =>
  shopTasks.value.filter((t) => t.status === 'available' && t.enabled)
)
const myShopTasks = computed(() =>
  shopTasks.value.filter((t) => t.status !== 'available')
)

function shopStatusLabel(status: string): string {
  const map: Record<string, string> = {
    accepted: '进行中',
    pending_review: '待确认',
    completed: '已完成',
  }
  return map[status] || status
}

function shopStatusLabelClass(status: string): string {
  const map: Record<string, string> = {
    accepted: 'bg-teal-200 text-teal-700',
    pending_review: 'bg-amber-200 text-amber-700',
    completed: 'bg-green-200 text-green-700',
  }
  return map[status] || ''
}

function taskStatusBg(status: string): string {
  if (status === 'completed') return 'border-green-300'
  if (status === 'pending_review') return 'border-amber-300'
  return ''
}

function goalCardClass(g: any): string {
  if (g.status === 'completed') return 'border-green-400 bg-green-50'
  if (g.status === 'approved') return 'border-teal-400 bg-teal-50'
  if (g.status === 'pending') return 'border-amber-400 bg-amber-50'
  if (g.status === 'rejected') return 'border-red-300 bg-red-50'
  return 'border-amber-300 bg-amber-50'
}

function goalStatusClass(g: any): string {
  const map: Record<string, string> = {
    completed: 'bg-green-200 text-green-700',
    approved: 'bg-teal-200 text-teal-700',
    pending: 'bg-amber-200 text-amber-700',
    rejected: 'bg-red-200 text-red-700',
  }
  return map[g.status] || ''
}

function goalStatusLabel(g: any): string {
  const map: Record<string, string> = {
    completed: '已达成',
    approved: '进行中',
    pending: '待审批',
    rejected: '未通过',
  }
  return map[g.status] || g.status
}

async function acceptShopTask(t: any) {
  shopLoading.value = true
  try {
    await api.acceptShopTask(t.id)
    playSound('click')
    toast.success(`已接取挑战「${t.title}」`)
    await loadShopTasks()
  } catch (e: any) {
    toast.error(e.message || '接取失败')
  } finally {
    shopLoading.value = false
  }
}

async function submitShopTask(t: any) {
  shopLoading.value = true
  try {
    await api.submitShopTask(t.id)
    playSound('click')
    toast.success('已提交，等待家长确认！')
    await loadShopTasks()
  } catch (e: any) {
    toast.error(e.message || '提交失败')
  } finally {
    shopLoading.value = false
  }
}

async function cancelShopTask(t: any) {
  shopLoading.value = true
  try {
    await api.cancelShopTask(t.id)
    playSound('click')
    toast.info('已取消挑战')
    await loadShopTasks()
  } catch (e: any) {
    toast.error(e.message || '取消失败')
  } finally {
    shopLoading.value = false
  }
}

async function createGoal() {
  if (!goalForm.value.title || !goalForm.value.target_score) return
  try {
    await api.createGoal({
      title: goalForm.value.title,
      target_score: goalForm.value.target_score,
      description: goalForm.value.description,
      deadline: goalForm.value.deadline || null,
    })
    showGoalForm.value = false
    goalForm.value = { title: '', target_score: 50, description: '', deadline: '' }
    playSound('click')
    toast.success('目标已设定！')
    await loadGoals()
  } catch (e: any) {
    toast.error(e.message || '创建目标失败')
  }
}

async function loadShopTasks() {
  try {
    shopTasks.value = await api.getShopTasks()
  } catch { /* ignore */ }
}

async function loadGoals() {
  try {
    goals.value = await api.getGoals()
  } catch { /* ignore */ }
}

async function load() {
  loading.value = true
  try {
    await store.loadCore()
    await Promise.all([loadShopTasks(), loadGoals()])
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.shop-card {
  background: linear-gradient(135deg, #fff8e1, #fff3cd);
  border: 2px solid #ffb74d;
}
.overlay-bg {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
}
</style>
