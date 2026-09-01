<template>
  <div>
    <h1 class="text-xl font-bold mb-4 pixel-font text-amber-900">积分记录</h1>

    <!-- 范围切换 -->
    <div class="flex gap-2 mb-4">
      <button
        v-for="r in ranges"
        :key="r.key"
        @click="range = r.key as any"
        class="px-3 py-1.5 rounded-lg text-xs font-bold pixel-btn transition-colors"
        :class="range === r.key ? 'bg-grass-500 text-white' : 'bg-amber-100 text-amber-700'"
      >
        {{ r.label }}
      </button>
    </div>

    <!-- 汇总条 -->
    <div class="pixel-card rounded-xl p-3 mb-4 flex items-center justify-between">
      <div class="text-sm text-amber-700">
        当前范围 <span class="font-bold text-amber-900">{{ rangeLabel }}</span>
      </div>
      <div class="text-sm">
        <span class="text-teal-600 font-bold">+{{ rangeStats.pos }}</span>
        <span class="text-amber-300 mx-1">/</span>
        <span class="text-red-500 font-bold">{{ rangeStats.neg }}</span>
        <span class="text-amber-400 ml-2 text-xs">净增</span>
        <span class="ml-2 font-bold" :class="rangeStats.net >= 0 ? 'text-teal-600' : 'text-red-500'">
          {{ rangeStats.net >= 0 ? '+' : '' }}{{ rangeStats.net }}
        </span>
      </div>
    </div>

    <!-- 按天分组的完整流水 -->
    <div class="space-y-4">
      <div
        v-for="g in grouped"
        :key="g.dateKey"
        class="pixel-card rounded-xl p-4"
      >
        <div class="flex items-center justify-between mb-3">
          <div class="font-bold text-amber-900">{{ g.dateLabel }}</div>
          <div class="text-xs">
            <span class="text-teal-600 font-bold">+{{ g.pos }}</span>
            <span class="text-amber-300 mx-1">/</span>
            <span class="text-red-500 font-bold">{{ g.neg }}</span>
            <span class="ml-2 font-bold" :class="g.net >= 0 ? 'text-teal-600' : 'text-red-500'">
              {{ g.net >= 0 ? '+' : '' }}{{ g.net }}
            </span>
          </div>
        </div>
        <div class="divide-y divide-amber-100">
          <div v-for="r in g.items" :key="r.id" class="py-2.5 flex items-center justify-between">
            <div class="flex-1 flex items-center gap-2 min-w-0">
              <PixelIcon type="gem" :size="16" class="shrink-0" />
              <div class="min-w-0">
                <div class="font-medium text-amber-900 truncate">{{ r.reason || typeLabel(r.record_type) }}</div>
                <div class="text-[10px] text-amber-500">
                  {{ formatTime(r.created_at) }} · {{ r.operator }}
                  <span class="ml-1 px-1 rounded bg-amber-100 text-amber-600">{{ typeLabel(r.record_type) }}</span>
                </div>
              </div>
            </div>
            <span
              class="font-bold px-2 py-1 rounded-lg shrink-0"
              :class="r.score_delta > 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
            >
              {{ r.score_delta > 0 ? '+' : '' }}{{ r.score_delta }}
            </span>
          </div>
        </div>
      </div>
      <div v-if="!grouped.length" class="pixel-card rounded-xl p-6 text-center text-amber-500">
        该时间段暂无积分记录
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api } from '@/api'
import PixelIcon from '@/components/game/PixelIcon.vue'

const ranges = [
  { key: '7d', label: '近7天', days: 7 },
  { key: '30d', label: '近30天', days: 30 },
  { key: 'all', label: '全部', days: 0 },
]
const range = ref<'7d' | '30d' | 'all'>('7d')
const records = ref<any[]>([])

const rangeLabel = computed(() => ranges.find(r => r.key === range.value)?.label || '')

function typeLabel(t: string): string {
  const map: Record<string, string> = {
    reward: '奖励', penalty: '惩罚', exchange: '兑换',
    adjust: '调整', checkin: '打卡', deposit: '存入', withdraw: '取出',
  }
  return map[t] || t
}

function formatTime(t: any) {
  if (!t) return ''
  const d = new Date(t)
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function dateKeyOf(t: any): string {
  const d = new Date(t)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const dayNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

function dateKey(t: any): string {
  return dateKeyOf(t)
}

const grouped = computed(() => {
  const days = ranges.find(r => r.key === range.value)?.days || 0
  const now = new Date()
  let list = records.value
  if (days > 0) {
    const cutoff = now.getTime() - days * 86400000
    list = list.filter(r => new Date(r.created_at).getTime() >= cutoff)
  }
  // 按日期分组，日期倒序
  const map = new Map<string, any[]>()
  for (const r of list) {
    const k = dateKey(r.created_at)
    if (!map.has(k)) map.set(k, [])
    map.get(k)!.push(r)
  }
  const keys = Array.from(map.keys()).sort((a, b) => b.localeCompare(a))
  return keys.map(k => {
    const items = map.get(k)!
    // 组内按时间倒序
    items.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    const pos = items.reduce((s, r) => s + (r.score_delta > 0 ? r.score_delta : 0), 0)
    const neg = items.reduce((s, r) => s + (r.score_delta < 0 ? r.score_delta : 0), 0)
    const [y, m, d] = k.split('-').map(Number)
    const dt = new Date(y, m - 1, d)
    const today = new Date()
    const isToday = y === today.getFullYear() && m - 1 === today.getMonth() && d === today.getDate()
    return {
      dateKey: k,
      dateLabel: `${m}月${d}日 ${dayNames[dt.getDay()]}${isToday ? '（今天）' : ''}`,
      pos,
      neg,
      net: pos + neg,
      items,
    }
  })
})

const rangeStats = computed(() => {
  let pos = 0, neg = 0
  for (const g of grouped.value) {
    pos += g.pos
    neg += g.neg
  }
  return { pos, neg, net: pos + neg }
})

onMounted(async () => {
  try {
    records.value = await api.getHistory(500)
  } catch (e) {
    console.error(e)
  }
})
</script>