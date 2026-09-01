/**
 * 资源映射表
 * 系统素材由独立资源库提供（frontend/public/assets/*），
 * 代码中不硬编码图片路径，统一通过资源映射引用。
 * 本阶段使用占位/无图降级，阶段3接入真实 PNG 素材。
 */

export const RESOURCE_BASE = '/assets'

// 角色头像映射
export const avatarMap: Record<string, string> = {
  'miner_default.png': `${RESOURCE_BASE}/avatar/miner_default.png`,
}

// 等级图标映射
export const levelIconMap: Record<string, string> = {
  level_1: `${RESOURCE_BASE}/avatar/level_1.png`,
  level_2: `${RESOURCE_BASE}/avatar/level_2.png`,
  level_3: `${RESOURCE_BASE}/avatar/level_3.png`,
  level_4: `${RESOURCE_BASE}/avatar/level_4.png`,
  level_5: `${RESOURCE_BASE}/avatar/level_5.png`,
  level_6: `${RESOURCE_BASE}/avatar/level_6.png`,
}

// 宝石
export const gemIcon = `${RESOURCE_BASE}/gem/gem.png`

// 徽章
export const badgeMap: Record<string, string> = {
  common: `${RESOURCE_BASE}/badge/badge_common.png`,
  rare: `${RESOURCE_BASE}/badge/badge_rare.png`,
  epic: `${RESOURCE_BASE}/badge/badge_epic.png`,
  legendary: `${RESOURCE_BASE}/badge/badge_legendary.png`,
}

// 任务类型图标
export const taskIconMap: Record<string, string> = {
  task_homework: `${RESOURCE_BASE}/ui/task_homework.png`,
  task_read: `${RESOURCE_BASE}/ui/task_read.png`,
  task_early: `${RESOURCE_BASE}/ui/task_early.png`,
  task_sport: `${RESOURCE_BASE}/ui/task_sport.png`,
  task_clean: `${RESOURCE_BASE}/ui/task_clean.png`,
}

// 奖励图标
export const rewardIconMap: Record<string, string> = {
  reward_tv: `${RESOURCE_BASE}/ui/reward_tv.png`,
  reward_tablet: `${RESOURCE_BASE}/ui/reward_tablet.png`,
  reward_snack: `${RESOURCE_BASE}/ui/reward_snack.png`,
  reward_toy: `${RESOURCE_BASE}/ui/reward_toy.png`,
}

// 音效
export const soundMap: Record<string, string> = {
  gem: `${RESOURCE_BASE}/sounds/gem.wav`,
  levelup: `${RESOURCE_BASE}/sounds/levelup.wav`,
  achievement: `${RESOURCE_BASE}/sounds/achievement.wav`,
  click: `${RESOURCE_BASE}/sounds/click.wav`,
}

/**
 * 解析资源路径（无素材时返回占位/空，阶段3完善）
 */
export function resolveAvatar(key?: string | null): string {
  if (!key) return ''
  return avatarMap[key] ?? ''
}

export function resolveLevelIcon(levelKey: string): string {
  return levelIconMap[levelKey] ?? ''
}

export function resolveBadge(rarity: string): string {
  return badgeMap[rarity] ?? badgeMap.common
}

export function resolveTaskIcon(key: string): string {
  return taskIconMap[key] ?? ''
}

export function resolveRewardIcon(key: string): string {
  return rewardIconMap[key] ?? ''
}