<template>
  <div>
    <h1 class="text-xl font-bold mb-4 pixel-font text-amber-900">数据看板</h1>

    <!-- 快捷加/减分 -->
    <div class="pixel-card rounded-xl p-4 mb-4">
      <h2 class="font-bold mb-3 text-amber-900 flex items-center gap-2">
        <PixelIcon type="task" task-type="习惯" :size="24" /> 快捷记录
      </h2>
      <div v-if="limitHint" class="text-xs text-red-600 mb-2 bg-red-50 px-3 py-1 rounded-lg">⚠ {{ limitHint }}</div>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="t in quickTasks"
          :key="t.id"
          class="pixel-btn px-3 py-2 rounded-lg text-sm"
          :class="t.score_value > 0 ? 'btn-grass' : 'btn-red'"
          :disabled="loading"
          @click="record(t)"
        >
          <PixelIcon type="task" :task-type="t.task_type" :size="16" class="mr-1" />
          {{ t.name }} {{ t.score_value > 0 ? '+' : '' }}{{ t.score_value }}
        </button>
      </div>
    </div>

    <!-- 银行存币卡片 -->
    <div class="pixel-card rounded-xl p-4 mb-4" v-if="bank">
      <h2 class="font-bold mb-2 text-amber-900 flex items-center gap-2">
        <PixelIcon type="badge" code="bank" :size="20" /> 银行存款
      </h2>
      <div class="flex items-center justify-between">
        <div>
          <div class="flex items-center gap-1 text-2xl font-bold text-teal-600">
            <PixelIcon type="gem" :size="22" />{{ bank.bank_balance }}
          </div>
          <div class="text-xs text-amber-700 mt-1">银行存币</div>
        </div>
        <div class="text-right space-y-1 text-xs text-amber-700">
          <div>利率 {{ bank.interest_rate }}% / 周</div>
          <div v-if="bank.today_interest > 0" class="text-green-600 font-bold">明日可增 +{{ bank.today_interest }}</div>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-2 gap-3 mb-4">
      <div class="pixel-card rounded-xl p-3 text-center">
        <div class="flex items-center justify-center gap-1 text-2xl font-bold text-teal-600">
          <PixelIcon type="gem" :size="20" />{{ dash?.today_score ?? 0 }}
        </div>
        <div class="text-xs text-amber-700 mt-1">今日积分</div>
      </div>
      <div class="pixel-card rounded-xl p-3 text-center">
        <div class="text-2xl font-bold text-orange-600">{{ dash?.week_score ?? 0 }}</div>
        <div class="text-xs text-amber-700 mt-1">本周积分</div>
      </div>
      <div class="pixel-card rounded-xl p-3 text-center">
        <div class="flex items-center justify-center gap-1 text-2xl font-bold text-teal-700">
          <PixelIcon type="gem" :size="20" />{{ dash?.total_score ?? 0 }}
        </div>
        <div class="text-xs text-amber-700 mt-1">当前余额</div>
      </div>
      <div class="pixel-card rounded-xl p-3 text-center">
        <div class="text-2xl font-bold text-purple-600">{{ dash?.lifetime_score ?? 0 }}</div>
        <div class="text-xs text-amber-700 mt-1">累计成长</div>
      </div>
    </div>

    <!-- 正负比例 -->
    <div class="pixel-card rounded-xl p-4 mb-4">
      <h2 class="font-bold mb-2 text-amber-900">正负行为</h2>
      <div class="flex h-6 rounded-full overflow-hidden border-2 border-amber-300">
        <div class="bg-gradient-to-r from-green-400 to-green-500 transition-all" :style="{ width: posPercent + '%' }"></div>
        <div class="bg-gradient-to-r from-red-400 to-red-500 transition-all" :style="{ width: negPercent + '%' }"></div>
      </div>
      <div class="flex justify-between text-xs mt-1 text-amber-700">
        <span>奖励 {{ dash?.positive_count ?? 0 }} 次</span>
        <span>惩罚 {{ dash?.negative_count ?? 0 }} 次</span>
      </div>
    </div>

    <!-- 成长曲线 -->
    <div class="pixel-card rounded-xl p-4 mb-4">
      <h2 class="font-bold mb-3 text-amber-900">成长曲线（近14天）</h2>
      <StatChart type="line" :data="trendData" />
    </div>

    <!-- 分类统计 + 成就完成率 -->
    <div class="grid grid-cols-2 gap-3 mb-4">
      <!-- 分类环形图 -->
      <div class="pixel-card rounded-xl p-3">
        <h2 class="font-bold mb-2 text-sm text-amber-900 text-center">分类统计</h2>
        <div class="flex justify-center">
          <StatChart
            type="donut"
            :segments="categorySegments"
            :center-label="`${categoryTotal}分`"
            center-sub-label="总获得"
          />
        </div>
        <div class="mt-2 space-y-1">
          <div v-for="(c, i) in dash?.category_breakdown || []" :key="i" class="flex items-center justify-between text-[10px]">
            <span class="flex items-center gap-1">
              <span class="w-2 h-2 rounded-full" :style="{ background: donutColors[i % donutColors.length] }"></span>
              {{ c.category }}
            </span>
            <span class="text-amber-700">{{ c.total_score }}分 / {{ c.count }}次</span>
          </div>
        </div>
      </div>
      <!-- 成就完成率 -->
      <div class="pixel-card rounded-xl p-3">
        <h2 class="font-bold mb-2 text-sm text-amber-900 text-center">成就完成率</h2>
        <div class="flex justify-center">
          <StatChart
            type="ring"
            :ratio="dash?.achievement_stats?.completion_rate || 0"
            :ring-sub-label="`${dash?.achievement_stats?.unlocked || 0}/${dash?.achievement_stats?.total || 0}`"
            ring-color="#7c4dff"
          />
        </div>
      </div>
    </div>

    <!-- 打卡确认 -->
    <div class="pixel-card rounded-xl p-4 mb-4">
      <h2 class="font-bold mb-3 text-amber-900 flex items-center gap-2">
        <PixelIcon type="task" task-type="习惯" :size="24" /> 打卡待确认
        <span v-if="pendingCheckins.length" class="text-xs bg-amber-200 text-amber-800 px-2 py-0.5 rounded-full">
          {{ pendingCheckins.length }} 条待确认
        </span>
      </h2>
      <div v-if="pendingCheckins.length" class="space-y-2">
        <div
          v-for="c in pendingCheckins"
          :key="c.id"
          class="flex items-center justify-between p-2 rounded-lg bg-amber-50"
        >
          <div>
            <div class="text-sm font-bold text-amber-900">{{ c.task_name }}</div>
            <div class="text-[10px] text-amber-600">{{ c.checkin_date }}</div>
          </div>
          <div class="flex items-center gap-2">
            <span class="font-bold text-sm text-green-700 px-2 py-1 rounded bg-green-100">+{{ c.score_value }}</span>
            <button
              @click="confirmCheckin(c)"
              :disabled="checkinLoading"
              class="pixel-btn btn-grass px-3 py-1.5 rounded-lg text-xs font-bold"
            >确认</button>
          </div>
        </div>
      </div>
      <div v-else class="text-center text-amber-500 text-sm py-3">暂无待确认的打卡</div>
    </div>

    <!-- 目标审批 -->
    <div class="pixel-card rounded-xl p-4">
      <h2 class="font-bold mb-3 text-amber-900 flex items-center gap-2">
        <PixelIcon type="badge" :size="24" /> 目标管理
      </h2>
      <div v-if="goals.length" class="space-y-3">
        <div
          v-for="g in goals"
          :key="g.id"
          class="rounded-lg p-3 border-2"
          :class="goalCardClass(g)"
        >
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <div class="font-bold text-sm text-amber-900">{{ g.title }}</div>
              <p v-if="g.description" class="text-xs text-amber-600 mt-1">{{ g.description }}</p>
              <div class="text-[10px] text-amber-500 mt-1">
                目标 {{ g.target_score }} 宝石 · 奖励 +{{ g.bonus_score }}
                <span v-if="g.deadline"> · 截止 {{ g.deadline }}</span>
              </div>
            </div>
            <span class="text-[10px] px-2 py-0.5 rounded-full font-bold whitespace-nowrap" :class="goalStatusClass(g)">
              {{ goalStatusLabel(g) }}
            </span>
          </div>
          <!-- 审批中：显示按钮 -->
          <div v-if="g.status === 'pending'" class="flex gap-2 mt-2">
            <button @click="approveGoal(g)" class="flex-1 pixel-btn btn-grass py-1.5 rounded-lg text-xs">通过</button>
            <button @click="rejectGoal(g)" class="flex-1 pixel-btn btn-red py-1.5 rounded-lg text-xs">拒绝</button>
          </div>
          <!-- 进行中/已完成：显示进度 -->
          <div v-if="g.status === 'approved' || g.status === 'completed'" class="mt-2">
            <div class="flex justify-between text-[10px] text-amber-700 mb-1">
              <span>{{ g.progress_score }} / {{ g.target_score }}</span>
              <span>{{ Math.round((g.progress_ratio || 0) * 100) }}%</span>
            </div>
            <div class="h-2 bg-amber-200 rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-500"
                :style="{ width: `${(g.progress_ratio || 0) * 100}%`, background: g.status === 'completed' ? '#22c55e' : '#0d9488' }"
              ></div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="text-center text-amber-500 text-sm py-3">暂无目标</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { api } from '@/api'
import { useAppStore } from '@/stores/app'
import { useEffectStore } from '@/stores/effect'
import { useToastStore } from '@/stores/toast'
import { playSound } from '@/utils/sound'
import PixelIcon from '@/components/game/PixelIcon.vue'
import StatChart from '@/components/game/StatChart.vue'

const store = useAppStore()
const effectStore = useEffectStore()
const toast = useToastStore()
const dash = ref<any>(null)
const bank = ref<any>(null)
const quickTasks = ref<any[]>([])
const goals = ref<any[]>([])
const pendingCheckins = ref<any[]>([])
const checkinLoading = ref(false)
const loading = ref(false)
const limitHint = ref('')

const donutColors = ['#0d9488', '#f59e0b', '#7c4dff', '#ef4444', '#3b82f6', '#84cc16']

const posPercent = computed(() => {
  const p = dash.value?.positive_count || 0
  const n = dash.value?.negative_count || 0
  const total = p + n
  return total ? Math.round((p / total) * 100) : 50
})
const negPercent = computed(() => 100 - posPercent.value)

const trendData = computed(() => {
  return (dash.value?.trend || []).map((d: any) => ({ label: d.date, value: d.score }))
})

const categorySegments = computed(() => {
  return (dash.value?.category_breakdown || []).map((c: any) => ({ label: c.category, value: c.total_score }))
})

const categoryTotal = computed(() => {
  return (dash.value?.category_breakdown || []).reduce((s: number, c: any) => s + c.total_score, 0)
})

function trendHeight(score: number) {
  const max = Math.max(...(dash.value?.trend || []).map((d: any) => d.score), 1)
  return Math.max((score / max) * 100, score > 0 ? 8 : 3)
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

async function record(t: any) {
  loading.value = true
  limitHint.value = ''
  try {
    const res = await api.addScore({ task_rule_id: t.id, reason: t.name })
    await store.refreshBalance()
    await loadDash()
    if (t.score_value > 0) {
      playSound('gem')
    } else {
      playSound('penalty')
    }
    effectStore.handleApiResponse(res)
    toast.success(`已记录「${t.name}」${t.score_value > 0 ? '+' : ''}${t.score_value}`)
  } catch (e: any) {
    limitHint.value = e.message || '记录失败'
    toast.error(e.message || '记录失败')
  } finally {
    loading.value = false
  }
}

async function approveGoal(g: any) {
  try {
    await api.approveGoal(g.id)
    playSound('click')
    await loadGoals()
  } catch (e: any) {
    toast.error(e.message || '审批失败')
  }
}

async function rejectGoal(g: any) {
  if (!confirm(`拒绝目标「${g.title}」？`)) return
  try {
    await api.rejectGoal(g.id)
    await loadGoals()
  } catch (e: any) {
    toast.error(e.message || '操作失败')
  }
}

async function loadGoals() {
  try {
    goals.value = await api.getGoals()
  } catch (e) {
    console.error(e)
  }
}

async function loadPendingCheckins() {
  try {
    pendingCheckins.value = await api.getPendingCheckins()
  } catch (e) {
    console.error(e)
  }
}

async function confirmCheckin(c: any) {
  checkinLoading.value = true
  try {
    const res = await api.confirmCheckin(c.id)
    playSound('gem')
    await store.refreshBalance()
    await loadDash()
    await loadPendingCheckins()
    effectStore.handleApiResponse(res.score_result)
    if (res.milestone_reward) {
      toast.success(res.milestone_reward.message)
      playSound('levelup')
    } else {
      toast.success(`已确认「${c.task_name}」+${c.score_value}`)
    }
  } catch (e: any) {
    toast.error(e.message || '确认失败')
  } finally {
    checkinLoading.value = false
  }
}

async function loadDash() {
  const [d, tasks, b] = await Promise.all([api.getDashboard(14), api.getTasks(), api.getBank()])
  dash.value = d
  quickTasks.value = tasks.filter((t: any) => t.enabled)
  bank.value = b
}

onMounted(async () => {
  try {
    await store.loadCore()
    await Promise.all([loadDash(), loadGoals(), loadPendingCheckins()])
  } catch (e) {
    console.error(e)
  }
})
</script>
