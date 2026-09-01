<template>
  <div>
    <!-- 顶部统计 -->
    <div class="pixel-card rounded-xl p-4 mb-4">
      <div class="flex items-center justify-between mb-2">
        <h2 class="font-bold text-amber-900 text-lg flex items-center gap-2">
          <span class="text-2xl">🏆</span> 成就图鉴
        </h2>
        <div class="text-right">
          <div class="text-2xl font-bold text-amber-700">{{ unlockedCount }}/{{ achievements.length }}</div>
          <div class="text-[10px] text-amber-500">已解锁</div>
        </div>
      </div>
      <!-- 总进度条 -->
      <div class="pixel-bar rounded" style="height: 14px;">
        <div
          class="pixel-bar-fill"
          :style="{ width: `${progressPercent}%` }"
        ></div>
      </div>
      <div class="text-[10px] text-amber-600 mt-1 text-center">
        完成度 {{ progressPercent }}%
      </div>
    </div>

    <!-- 类别筛选 -->
    <div class="flex flex-wrap gap-2 mb-4">
      <button
        v-for="f in filters"
        :key="f.key"
        @click="activeFilter = f.key"
        class="pixel-btn px-3 py-1.5 rounded-lg text-xs whitespace-nowrap"
        :class="activeFilter === f.key ? 'btn-grass' : 'btn-wood'"
      >
        {{ f.icon }} {{ f.label }}
        <span class="ml-1 opacity-60">{{ filterCount(f.key) }}</span>
      </button>
    </div>

    <!-- 按类别分区的成就网格 -->
    <div v-for="grp in groupedAchievements" :key="grp.category" class="pixel-card rounded-xl p-4 mb-4">
      <div class="text-xs font-bold text-amber-700 mb-3 flex items-center gap-1">
        <span>{{ grp.icon }}</span> {{ grp.label }}
        <span class="text-[10px] text-amber-400 font-normal ml-1">
          {{ grp.list.filter((a:any)=>a.unlocked).length }}/{{ grp.list.length }} 已解锁
        </span>
      </div>
      <!-- 网格布局：自动换行，不横向滚动 -->
      <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
        <div
          v-for="a in grp.list"
          :key="a.id"
          class="text-center cursor-pointer"
          @click="openDetail(a)"
        >
          <!-- 徽章图标 -->
          <div
            class="badge-frame mx-auto mb-1 relative"
            :class="a.unlocked ? '' : 'badge-locked'"
            :style="a.unlocked ? badgeGlowStyle(a) : ''"
          >
            <PixelIcon
              v-if="a.unlocked"
              type="badge"
              :code="a.code"
              :tier="a.current_tier || 1"
              :size="40"
            />
            <span v-else class="text-2xl">🔒</span>
            <!-- 段位角标 -->
            <span
              v-if="a.unlocked"
              class="absolute -top-1.5 -right-1.5 text-[8px] px-1.5 py-0.5 rounded-full font-bold"
              :style="{ background: a.tier_color, color: a.current_tier >= 3 ? '#5b4a00' : '#fff' }"
            >{{ a.tier_label }}</span>
          </div>
          <div class="text-[11px] text-amber-800 font-medium truncate">{{ a.name }}</div>
          <!-- 段位进度：当前段位 → 下一段位 -->
          <div v-if="a.unlocked && a.next_threshold" class="mt-1">
            <div class="h-1.5 bg-amber-200 rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-500"
                :style="{ width: `${(a.progress_ratio || 0) * 100}%`, background: a.tier_color || '#ffd54f' }"
              ></div>
            </div>
            <div class="text-[9px] text-amber-600 mt-0.5">
              {{ a.current_tier < a.max_tier ? `${a.progress}/${a.next_threshold} → ${nextTierLabel(a)}` : '★ 满级' }}
            </div>
          </div>
          <!-- 未解锁：首段位进度 -->
          <div v-else-if="!a.unlocked && a.next_threshold" class="mt-1">
            <div class="h-1.5 bg-amber-200 rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-500"
                :style="{ width: `${(a.progress_ratio || 0) * 100}%`, background: a.tier_color || '#ffd54f' }"
              ></div>
            </div>
            <div class="text-[9px] text-amber-600 mt-0.5">{{ a.progress }}/{{ a.next_threshold }}</div>
          </div>
          <div v-else class="text-[9px] mt-0.5 font-bold" :style="{ color: a.tier_color || '#ffd54f' }">
            ✓ {{ a.tier_label }}
          </div>
        </div>
      </div>
      <EmptyState v-if="!grp.list.length" icon="🎖️" text="该分类下暂无成就" />
    </div>

    <!-- 成就详情弹窗 -->
    <div v-if="selectedAch" class="fixed inset-0 flex items-center justify-center p-4 z-30" @click="selectedAch = null">
      <div class="overlay-bg"></div>
      <div
        class="pixel-card rounded-xl p-6 relative max-w-xs w-full text-center"
        :style="selectedAch.unlocked ? detailBorderStyle(selectedAch) : ''"
        @click.stop
      >
        <!-- 大徽章 -->
        <div
          class="badge-frame-large mx-auto mb-3"
          :class="selectedAch.unlocked ? '' : 'badge-locked'"
          :style="selectedAch.unlocked ? badgeGlowStyle(selectedAch) : ''"
        >
          <PixelIcon
            v-if="selectedAch.unlocked"
            type="badge"
            :code="selectedAch.code"
            :tier="selectedAch.current_tier || 1"
            :size="56"
          />
          <span v-else class="text-4xl">🔒</span>
        </div>

        <!-- 名称 + 类别 -->
        <div class="font-bold text-lg text-amber-900">{{ selectedAch.name }}</div>
        <span
          class="inline-block text-[10px] px-2 py-0.5 rounded-full font-bold mt-1"
          :style="{ background: selectedAch.tier_color || '#ffd54f', color: selectedAch.current_tier >= 3 ? '#5b463a' : '#fff' }"
        >{{ selectedAch.category_icon }} {{ selectedAch.category_label }}</span>

        <!-- 描述 -->
        <p class="text-sm text-amber-700 mt-2">{{ selectedAch.description }}</p>

        <!-- 段位一览 -->
        <div class="mt-3 text-left">
          <div class="text-xs font-bold text-amber-700 mb-2 flex items-center justify-between">
            <span>段位进度</span>
            <span class="text-[10px] text-amber-500">当前：{{ selectedAch.tier_label }}</span>
          </div>
          <div class="space-y-1.5">
<div
              v-for="(item, idx) in selectedAch.tier_thresholds"
              :key="idx"
              class="flex items-center gap-2 rounded-lg px-2 py-1.5"
              :class="idx + 1 <= selectedAch.current_tier ? 'bg-green-50' : 'bg-amber-50'"
            >
              <span
                class="text-[10px] font-bold px-2 py-0.5 rounded-full shrink-0"
                :style="idx + 1 <= selectedAch.current_tier
                  ? { background: tierColorOf(idx+1), color: idx+1>=3?'#5b463a':'#fff' }
                  : { background: '#e5e5e5', color: '#999' }"
              >{{ tierLabelOf(idx+1) }}</span>
              <span class="text-[10px] text-amber-700 flex-1">达 {{ item }} 步</span>
              <span v-if="idx + 1 <= selectedAch.current_tier" class="text-xs text-green-600 font-bold">✓</span>
              <span v-else class="text-[10px] text-amber-500">
                {{ selectedAch.progress }}/{{ item }}
              </span>
            </div>
          </div>
        </div>

        <!-- 解锁时间 -->
        <div v-if="selectedAch.unlocked" class="mt-3 text-[10px] text-amber-500">
          {{ formatDate(selectedAch.unlocked_at) }}
        </div>

        <button @click="selectedAch = null" class="mt-4 pixel-btn btn-grass px-6 py-2 rounded-lg w-full">
          知道了
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import PixelIcon from '@/components/game/PixelIcon.vue'
import EmptyState from '@/components/game/EmptyState.vue'
import Skeleton from '@/components/game/Skeleton.vue'
import { api } from '@/api'
import { useAppStore } from '@/stores/app'
import { playSound } from '@/utils/sound'

const store = useAppStore()
const achievements = ref<any[]>([])
const loading = ref(false)
const selectedAch = ref<any>(null)
const activeFilter = ref('all')

// 类别筛选（使用 API 返回的 category）
const filters = [
  { key: 'all', label: '全部', icon: '📋' },
  { key: 'study', label: '学习', icon: '📖' },
  { key: 'chore', label: '家务', icon: '🧹' },
  { key: 'habit', label: '习惯', icon: '⏰' },
  { key: 'score', label: '积分', icon: '💎' },
  { key: 'exchange', label: '兑换', icon: '🎁' },
  { key: 'challenge', label: '挑战', icon: '⚔️' },
  { key: 'checkin', label: '打卡', icon: '📅' },
  { key: 'goal', label: '目标', icon: '🚩' },
  { key: 'bank', label: '银行', icon: '🐷' },
]

const TIER_LABELS = ['', '青铜', '白银', '黄金', '钻石']
const TIER_COLORS = ['', '#cd7f32', '#c0c0c0', '#ffd700', '#b9f2ff']
const CATEGORY_ICONS: Record<string, string> = {
  study: '📖', chore: '🧹', habit: '⏰', score: '💎', exchange: '🎁',
  challenge: '⚔️', checkin: '📅', goal: '🚩', bank: '🐷',
}
const CATEGORY_LABELS: Record<string, string> = {
  study: '学习', chore: '家务', habit: '习惯', score: '积分', exchange: '兑换',
  challenge: '挑战', checkin: '打卡', goal: '目标', bank: '银行',
}

const unlockedCount = computed(() => achievements.value.filter((a) => a.unlocked).length)
const progressPercent = computed(() => {
  if (!achievements.value.length) return 0
  return Math.round((unlockedCount.value / achievements.value.length) * 100)
})

function tierLabelOf(t: number): string {
  return TIER_LABELS[t] || ''
}
function tierColorOf(t: number): string {
  return TIER_COLORS[t] || '#cd7f32'
}
function nextTierLabel(cur: number): string {
  return tierLabelOf(cur + 1)
}

// 分组展示：按类别分区（支持筛选）
const groupedAchievements = computed(() => {
  const source = activeFilter.value === 'all'
    ? achievements.value
    : achievements.value.filter((a) => a.category === activeFilter.value)

  // 按类别分组，保持 filters 顺序
  const order = ['study', 'chore', 'habit', 'score', 'exchange', 'challenge', 'checkin', 'goal', 'bank']
  const groups: any[] = []
  for (const cat of order) {
    const list = source.filter((a) => a.category === cat)
    if (list.length) {
      groups.push({
        category: cat,
        label: CATEGORY_LABELS[cat] || '其他',
        icon: CATEGORY_ICONS[cat] || '🏅',
        list,
      })
    }
  }
  return groups
})

function filterCount(key: string): number {
  if (key === 'all') return achievements.value.length
  return achievements.value.filter((a) => a.category === key).length
}

function badgeGlowStyle(a: any): Record<string, string> {
  const color = a.tier_color || a.rarity_glow
  if (!color) return {}
  const intensity = a.tier_intensity || 'low'
  const spread = intensity === 'legendary' ? '10px' : intensity === 'high' ? '6px' : intensity === 'medium' ? '4px' : '2px'
  return {
    boxShadow: `0 0 ${spread} ${color}, 0 0 ${parseInt(spread) * 2}px ${color}40`,
    borderColor: color,
    background: `linear-gradient(135deg, ${color}15, ${color}30)`,
  }
}

function detailBorderStyle(a: any): Record<string, string> {
  const color = a.tier_color || a.rarity_glow
  return color ? { borderColor: color } : {}
}

function formatDate(dt: any): string {
  if (!dt) return ''
  try {
    const d = new Date(dt)
    return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 解锁`
  } catch {
    return ''
  }
}

function openDetail(a: any) {
  selectedAch.value = a
  playSound('click')
}

async function load() {
  loading.value = true
  try {
    await store.loadCore()
    achievements.value = await api.getAchievements()
  } catch (e: any) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.badge-frame {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid #ffd54f;
  border-radius: 10px;
  background: linear-gradient(135deg, #fff8e1, #fff3cd);
  transition: transform 0.2s;
}

.badge-frame:active {
  transform: scale(0.95);
}

.badge-frame-large {
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 4px solid #ffd54f;
  border-radius: 14px;
  background: linear-gradient(135deg, #fff8e1, #fff3cd);
}

.badge-locked {
  border-color: #bdbdbd;
  background: linear-gradient(135deg, #f5f5f5, #e0e0e0);
  opacity: 0.6;
}

.overlay-bg {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
}
</style>