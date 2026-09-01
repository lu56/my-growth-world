import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { playSound } from '@/utils/sound'

interface LevelUpInfo {
  old_level: number
  old_level_name: string
  new_level: number
  new_level_name: string
  new_level_icon: string
  new_level_description: string
}

interface AchievementInfo {
  name: string
  code: string
  rarity: string
  rarity_label?: string
  rarity_glow?: string
  description: string
  tier_label?: string
  tier_color?: string
  old_tier?: number
  new_tier?: number
  current_tier?: number
  is_upgrade?: boolean
}

export const useEffectStore = defineStore('effect', () => {
  const levelUpInfo = ref<LevelUpInfo | null>(null)
  const achievementList = ref<AchievementInfo[]>([])
  const showConfetti = ref(false)

  function triggerLevelUp(info: LevelUpInfo) {
    levelUpInfo.value = info
    playSound('levelup')
    triggerConfetti()
  }

  function triggerAchievements(list: AchievementInfo[]) {
    if (list && list.length > 0) {
      achievementList.value = list
      playSound('achievement')
      triggerConfetti()
    }
  }

  function triggerConfetti() {
    showConfetti.value = true
    setTimeout(() => { showConfetti.value = false }, 3500)
  }

  function clearLevelUp() {
    levelUpInfo.value = null
  }

  function clearAchievements() {
    achievementList.value = []
  }

  function clearAll() {
    levelUpInfo.value = null
    achievementList.value = []
    showConfetti.value = false
  }

  /**
   * 统一处理 API 返回的 level_change 和 new_achievements
   * 先触发成就（如果有），延迟触发等级升级
   */
  function handleApiResponse(data: any) {
    if (data?.new_achievements && data.new_achievements.length > 0) {
      triggerAchievements(data.new_achievements)
    }
    if (data?.level_change?.level_up) {
      // 延迟 1.5s 触发等级升级（让成就动画先播放）
      setTimeout(() => triggerLevelUp(data.level_change), 1500)
    }
  }

  return {
    levelUpInfo,
    achievementList,
    showConfetti,
    triggerLevelUp,
    triggerAchievements,
    triggerConfetti,
    clearLevelUp,
    clearAchievements,
    clearAll,
    handleApiResponse,
  }
})
