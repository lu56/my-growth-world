<template>
  <div>
    <HeroCard />

    <!-- 成长进度条 -->
    <div class="pixel-card rounded-xl p-4 mb-4">
      <div class="flex justify-between text-sm mb-2">
        <span class="text-orange-800 font-bold">距离 {{ level?.next_level_name || '顶级' }}</span>
        <span class="text-amber-700">{{ level?.lifetime_score || 0 }} 宝石</span>
      </div>
      <div class="pixel-bar rounded">
        <div
          class="pixel-bar-fill"
          :style="{ width: `${(level?.progress || 0) * 100}%` }"
        ></div>
      </div>
      <div class="text-amber-700 text-xs mt-1" v-if="level?.next_min_score">
        下一等级需 {{ level.next_min_score }} 宝石
      </div>
    </div>

    <!-- 每日打卡 -->
    <div class="pixel-card rounded-xl p-4 mb-4">
      <div class="flex justify-between items-center mb-3">
        <h2 class="font-bold text-amber-900 text-lg flex items-center gap-2">
          <PixelIcon type="task" task-type="习惯" :size="24" /> 每日打卡
        </h2>
        <span v-if="checkinTasks.length" class="text-xs bg-teal-100 px-2 py-1 rounded-full text-teal-700 font-bold">
          已打 {{ checkedCount }}/{{ checkinTasks.length }}
        </span>
      </div>
      <div v-if="checkinTasks.length" class="space-y-2">
        <div
          v-for="t in checkinTasks"
          :key="t.task_rule_id"
          class="flex items-center justify-between p-2 rounded-lg"
          :class="t.checked_in_today ? 'bg-green-50' : 'bg-amber-50'"
        >
          <div class="flex items-center gap-2">
            <div
              class="w-9 h-9 rounded-lg flex items-center justify-center text-lg"
              :class="t.checked_in_today ? 'bg-green-200' : 'bg-amber-200'"
            >
              {{ t.checked_in_today ? '\u2713' : '\u25CB' }}
            </div>
            <div>
              <div class="text-sm font-bold text-amber-900">{{ t.task_name }}</div>
              <div class="text-[10px] text-amber-600">
                连续 {{ t.current_streak }} 天 · 最长 {{ t.longest_streak }} 天
              </div>
            </div>
          </div>
          <!-- 未提交：申请打卡 -->
          <button
            v-if="!t.checked_in_today"
            class="pixel-btn btn-grass px-3 py-1.5 rounded-lg text-xs font-bold"
            :disabled="checkinLoading"
            @click="requestCheckin(t)"
          >
            申请 +{{ t.score_value }}
          </button>
          <!-- 已提交待确认 -->
          <span v-else-if="t.status === 'pending'" class="text-amber-600 text-xs font-bold">
            待家长确认
          </span>
          <!-- 已确认 -->
          <span v-else class="text-green-600 text-xs font-bold">已完成</span>
        </div>
      </div>
      <EmptyState v-else icon="\u23F0" text="暂无打卡任务" />

      <!-- 里程碑提示 -->
      <div v-if="nextMilestone" class="mt-3 bg-purple-50 rounded-lg p-2 text-center">
        <span class="text-xs text-purple-700">
          再坚持 {{ nextMilestone.days - maxStreak }} 天，奖励 {{ nextMilestone.bonus }} 颗宝石！
        </span>
      </div>
    </div>

    <!-- 成长简报 -->
    <div class="pixel-card rounded-xl p-4 mb-4" v-if="report">
      <div class="flex justify-between items-center mb-3">
        <h2 class="font-bold text-amber-900 text-lg flex items-center gap-2">
          <span class="text-2xl">📋</span> 成长简报
        </h2>
        <span class="text-xs text-amber-600">{{ report.date_range }}</span>
      </div>
      <!-- 鼓励语 -->
      <div class="bg-gradient-to-r from-amber-100 to-teal-50 rounded-lg p-3 mb-3 text-center">
        <p class="text-sm font-bold text-teal-700">{{ report.encouragement }}</p>
      </div>
      <!-- 数据汇总 -->
      <div class="grid grid-cols-4 gap-2 mb-3">
        <div class="bg-teal-50 rounded-lg p-2 text-center">
          <div class="text-lg font-bold text-teal-600">{{ report.summary.total_score }}</div>
          <div class="text-[9px] text-amber-700">本周积分</div>
        </div>
        <div class="bg-orange-50 rounded-lg p-2 text-center">
          <div class="text-lg font-bold text-orange-600">{{ report.summary.task_count }}</div>
          <div class="text-[9px] text-amber-700">完成任务</div>
        </div>
        <div class="bg-purple-50 rounded-lg p-2 text-center">
          <div class="text-lg font-bold text-purple-600">{{ report.summary.checkin_days }}</div>
          <div class="text-[9px] text-amber-700">打卡天数</div>
        </div>
        <div class="bg-blue-50 rounded-lg p-2 text-center">
          <div class="text-lg font-bold text-blue-600">{{ report.summary.exchange_count }}</div>
          <div class="text-[9px] text-amber-700">兑换次数</div>
        </div>
      </div>
      <!-- 与上周对比 -->
      <div class="flex items-center justify-between text-xs mb-3" v-if="report.comparison">
        <span class="text-amber-600">对比上周</span>
        <span :class="report.comparison.score_change >= 0 ? 'text-green-600' : 'text-red-500'" class="font-bold">
          {{ report.comparison.score_change >= 0 ? '+' : '' }}{{ report.comparison.score_change }}
          ({{ report.comparison.score_change_pct }}%)
        </span>
      </div>
      <!-- 每日趋势 mini chart -->
      <div class="mb-3">
        <div class="text-[10px] text-amber-600 font-bold mb-1">每日趋势</div>
        <div class="flex items-end justify-between gap-1 h-16">
          <div
            v-for="d in report.daily_trend"
            :key="d.date"
            class="flex-1 flex flex-col items-center justify-end"
          >
            <div
              class="w-full rounded-t transition-all duration-500"
              :style="{
                height: `${Math.max(4, (d.score / maxDailyScore) * 48)}px`,
                background: d.score > 0 ? 'linear-gradient(180deg, #4dd0e1, #26c6da)' : '#e0e0e0'
              }"
            ></div>
            <div class="text-[8px] text-amber-500 mt-0.5">{{ d.weekday }}</div>
          </div>
        </div>
      </div>
      <!-- Top任务 -->
      <div v-if="report.top_tasks?.length" class="mb-2">
        <div class="text-[10px] text-amber-600 font-bold mb-1">最常完成</div>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="(t, i) in report.top_tasks"
            :key="i"
            class="text-[10px] bg-amber-100 px-2 py-1 rounded-full text-amber-700"
          >
            {{ i + 1 }}. {{ t.name }} ({{ t.count }})
          </span>
        </div>
      </div>
    </div>

    <!-- 里程碑弹窗 -->
    <div v-if="milestonePopup" class="fixed inset-0 flex items-center justify-center p-4 z-30" @click="milestonePopup = null">
      <div class="overlay-bg"></div>
      <div class="pixel-card rounded-xl p-6 relative max-w-xs w-full text-center" @click.stop>
        <div class="text-4xl mb-2">🎉</div>
        <h3 class="font-bold text-lg text-purple-700 mb-2">{{ milestonePopup.message }}</h3>
        <div class="flex items-center justify-center gap-1 text-2xl font-bold text-teal-600">
          <PixelIcon type="gem" :size="24" /> +{{ milestonePopup.bonus }}
        </div>
        <button @click="milestonePopup = null" class="mt-4 pixel-btn btn-grass px-6 py-2 rounded-lg w-full">
          太棒了！
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import HeroCard from '@/components/game/HeroCard.vue'
import PixelIcon from '@/components/game/PixelIcon.vue'
import EmptyState from '@/components/game/EmptyState.vue'
import { api } from '@/api'
import { useAppStore } from '@/stores/app'
import { useToastStore } from '@/stores/toast'

const store = useAppStore()
const toast = useToastStore()

const level = ref<any>(null)
const checkinTasks = ref<any[]>([])
const checkinLoading = ref(false)
const milestonePopup = ref<any>(null)
const report = ref<any>(null)

const checkedCount = computed(() => checkinTasks.value.filter((t) => t.checked_in_today).length)
const maxStreak = computed(() => Math.max(0, ...checkinTasks.value.map((t) => t.current_streak)))

const MILESTONES = [
  { days: 3, bonus: 5 },
  { days: 7, bonus: 15 },
  { days: 15, bonus: 30 },
  { days: 30, bonus: 100 },
]

const nextMilestone = computed(() => {
  for (const m of MILESTONES) {
    if (maxStreak.value < m.days) return m
  }
  return null
})

const maxDailyScore = computed(() => {
  if (!report.value?.daily_trend) return 1
  const max = Math.max(...report.value.daily_trend.map((d: any) => d.score))
  return max || 1
})

async function requestCheckin(t: any) {
  checkinLoading.value = true
  try {
    const res = await api.requestCheckin(t.task_rule_id)
    t.checked_in_today = true
    t.status = 'pending'
    t.checkin_id = res.checkin.id
    toast.success('已申请打卡，等待家长确认')
  } catch (e: any) {
    toast.error(e.message || '打卡申请失败')
  } finally {
    checkinLoading.value = false
  }
}

async function load() {
  try {
    await store.loadCore()
    const [lp, checkin, rpt] = await Promise.all([
      api.getLevelProgress(),
      api.getCheckinToday(),
      api.getWeeklyReport(0),
    ])
    level.value = lp
    checkinTasks.value = checkin
    report.value = rpt
  } catch (e: any) {
    console.error(e)
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
