<template>
  <Teleport to="body">
    <!-- 彩屑动画 -->
    <div v-if="effectStore.showConfetti" class="fixed inset-0 pointer-events-none z-40 overflow-hidden">
      <div
        v-for="i in 50"
        :key="i"
        class="confetti"
        :style="confettiStyle(i)"
      ></div>
    </div>

    <!-- 等级升级动画 -->
    <div v-if="effectStore.levelUpInfo" class="fixed inset-0 z-50 flex items-center justify-center anim-fade-in" @click="effectStore.clearLevelUp()">
      <div class="overlay-bg"></div>
      <div class="level-up-card relative anim-bounce-in" @click.stop>
        <!-- 金光散射粒子 -->
        <div class="particles-container">
          <div
            v-for="i in 20"
            :key="i"
            class="particle"
            :style="particleStyle(i)"
          >✦</div>
        </div>
        <div class="relative z-10 text-center p-8">
          <PixelIcon type="avatar" :level="effectStore.levelUpInfo.new_level" :size="64" class="anim-float mb-3" />
          <div class="text-yellow-400 text-sm font-bold tracking-widest mb-1 pixel-font">LEVEL UP!</div>
          <div class="text-3xl font-bold pixel-font text-amber-900 mb-1">
            Lv.{{ effectStore.levelUpInfo.new_level }}
          </div>
          <div class="text-xl font-bold text-orange-800 mb-2">{{ effectStore.levelUpInfo.new_level_name }}</div>
          <div class="text-amber-800 text-sm mb-3">{{ effectStore.levelUpInfo.new_level_description }}</div>
          <div class="text-xs text-amber-700">从「{{ effectStore.levelUpInfo.old_level_name }}」升级而来</div>
          <div class="mt-4 text-amber-600 text-sm anim-pulse">点击关闭</div>
        </div>
      </div>
    </div>

    <!-- 成就解锁动画（逐个展示） -->
    <div
      v-if="effectStore.achievementList.length > 0"
      class="fixed inset-0 z-50 flex items-center justify-center anim-fade-in"
      @click="effectStore.clearAchievements()"
    >
      <div class="overlay-bg"></div>
      <div
        class="ach-card relative anim-bounce-in"
        :style="achCardStyle"
        @click.stop
      >
        <!-- 旋转光效背景 -->
        <div
          class="absolute inset-0 opacity-20 anim-rotate-slow rounded-2xl"
          :style="{ background: `conic-gradient(from 0deg, ${currentAch.rarity_glow || '#ffd54f'}, transparent, ${currentAch.rarity_glow || '#ffd54f'}, transparent)` }"
        ></div>
        <div class="relative z-10 text-center p-8">
          <PixelIcon
            type="badge"
            :code="currentAch.code"
            :tier="currentAch.new_tier || currentAch.current_tier || 1"
            :size="56"
            class="anim-float mb-3"
          />
          <div class="text-xs font-bold tracking-widest mb-2 pixel-font" :style="{ color: currentAch.tier_color || currentAch.rarity_glow || '#ffd54f' }">
            {{ currentAch.is_upgrade ? '成就升级' : '成就解锁' }} · {{ currentAch.tier_label || currentAch.rarity_label || '普通' }}
          </div>
          <div class="text-2xl font-bold pixel-font text-amber-900 mb-2">{{ currentAch.name }}</div>
          <div class="text-amber-700 text-sm">{{ currentAch.description }}</div>
          <div v-if="currentAch.is_upgrade" class="mt-2 text-xs font-bold" :style="{ color: currentAch.tier_color || '#ffd54f' }">
            {{ tierLabelOf(currentAch.old_tier || 0) }} → {{ tierLabelOf(currentAch.new_tier || 0) }}
          </div>
          <div v-if="effectStore.achievementList.length > 1" class="mt-3 text-xs text-amber-600">
            还有 {{ effectStore.achievementList.length - 1 }} 个成就待查看
          </div>
          <div class="mt-4 text-xs text-amber-600 anim-pulse">点击查看下一个 / 关闭</div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useEffectStore } from '@/stores/effect'
import PixelIcon from './PixelIcon.vue'

const effectStore = useEffectStore()

const currentAch = computed(() => {
  return effectStore.achievementList[0] || {
    name: '',
    code: '',
    rarity: 'common',
    description: '',
    tier_label: '',
  }
})

const TIER_LABELS = ['', '青铜', '白银', '黄金', '钻石']
function tierLabelOf(t: number): string {
  return TIER_LABELS[t] || ''
}

const achCardStyle = computed(() => ({
  '--glow-color': currentAch.value.tier_color || currentAch.value.rarity_glow || '#ffd54f',
}))

function particleStyle(i: number): Record<string, string> {
  const angle = (i / 20) * Math.PI * 2
  const dist = 80 + (i % 3) * 40
  const tx = Math.cos(angle) * dist + 'px'
  const ty = Math.sin(angle) * dist + 'px'
  const colors = ['#ffd54f', '#ffb300', '#ff8f00', '#fff176']
  return {
    '--tx': tx,
    '--ty': ty,
    color: colors[i % colors.length],
    fontSize: (10 + (i % 3) * 4) + 'px',
    left: '50%',
    top: '50%',
    animationDelay: (i * 0.02) + 's',
  }
}

function confettiStyle(i: number): Record<string, string> {
  const colors = ['#7cb342', '#26c6da', '#ffd54f', '#ab47bc', '#ef5350', '#4fc3f7']
  const left = Math.random() * 100 + '%'
  const delay = Math.random() * 0.8 + 's'
  const duration = (2.5 + Math.random() * 1.5) + 's'
  const size = (6 + Math.random() * 6) + 'px'
  const color = colors[i % colors.length]
  return {
    left,
    width: size,
    height: size,
    background: color,
    borderRadius: Math.random() > 0.5 ? '50%' : '2px',
    animationDelay: delay,
    animationDuration: duration,
  }
}
</script>

<style scoped>
.overlay-bg {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
}

.level-up-card {
  background: linear-gradient(135deg, #fff8e1 0%, #fff3cd 50%, #ffe082 100%);
  border: 4px solid #ffb300;
  border-radius: 16px;
  box-shadow: 0 0 40px rgba(255, 179, 0, 0.5), 0 8px 0 #e65100;
  max-width: 320px;
  margin: 0 16px;
  overflow: hidden;
}

.ach-card {
  background: linear-gradient(135deg, #fff8e1 0%, #fff3cd 100%);
  border: 4px solid;
  border-color: var(--glow-color, #ffd54f);
  border-radius: 16px;
  box-shadow: 0 0 30px var(--glow-color, #ffd54f), 0 8px 0 rgba(0,0,0,0.2);
  max-width: 300px;
  margin: 0 16px;
  overflow: hidden;
}

.particles-container {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.anim-fade-in { animation: fadeIn 0.3s ease; }
.anim-bounce-in { animation: bounceIn 0.5s cubic-bezier(0.68, -0.55, 0.27, 1.55); }
.anim-float { animation: float 2s ease-in-out infinite; }
.anim-pulse { animation: pulse 1.5s ease-in-out infinite; }
.anim-rotate-slow { animation: rotateSlow 8s linear infinite; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes bounceIn {
  0% { transform: scale(0.3); opacity: 0; }
  50% { transform: scale(1.05); opacity: 1; }
  70% { transform: scale(0.95); }
  100% { transform: scale(1); }
}
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
@keyframes pulse { 0%, 100% { opacity: 0.4; } 50% { opacity: 1; } }
@keyframes rotateSlow { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
</style>
