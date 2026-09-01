<template>
  <span class="pixel-icon inline-flex items-center justify-center" :style="{ width: size + 'px', height: size + 'px' }">
    <!-- 等级角色头像 -->
    <svg v-if="type === 'avatar'" :width="size" :height="size" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg" shape-rendering="crispEdges">
      <!-- 16x16 像素角色，根据 level 变化配色和装饰 -->
      <template v-if="level <= 1">
        <!-- Lv1 成长新人：绿色帽子 + 棕衣 -->
        <rect x="5" y="1" width="6" height="1" fill="#66bb6a" />
        <rect x="4" y="2" width="8" height="1" fill="#43a047" />
        <rect x="4" y="3" width="8" height="2" fill="#ffe0b2" />
        <rect x="5" y="3" width="1" height="1" fill="#5d4037" />
        <rect x="10" y="3" width="1" height="1" fill="#5d4037" />
        <rect x="6" y="5" width="4" height="1" fill="#ffe0b2" />
        <rect x="3" y="6" width="10" height="4" fill="#8d6e63" />
        <rect x="6" y="7" width="1" height="1" fill="#ffd54f" />
        <rect x="9" y="7" width="1" height="1" fill="#ffd54f" />
        <rect x="3" y="10" width="10" height="2" fill="#6d4c41" />
        <rect x="4" y="12" width="8" height="2" fill="#5d4037" />
        <rect x="5" y="14" width="6" height="1" fill="#3e2723" />
      </template>
      <template v-else-if="level === 2">
        <!-- Lv2 森林探索者：蓝帽 + 皮甲 -->
        <rect x="5" y="1" width="6" height="1" fill="#4fc3f7" />
        <rect x="4" y="2" width="8" height="1" fill="#0288d1" />
        <rect x="4" y="3" width="8" height="2" fill="#ffe0b2" />
        <rect x="5" y="3" width="1" height="1" fill="#5d4037" />
        <rect x="10" y="3" width="1" height="1" fill="#5d4037" />
        <rect x="6" y="5" width="4" height="1" fill="#ffe0b2" />
        <rect x="3" y="6" width="10" height="4" fill="#a1887f" />
        <rect x="5" y="6" width="2" height="1" fill="#5d4037" />
        <rect x="6" y="7" width="1" height="1" fill="#26c6da" />
        <rect x="9" y="7" width="1" height="1" fill="#26c6da" />
        <rect x="3" y="10" width="10" height="2" fill="#8d6e63" />
        <rect x="4" y="12" width="8" height="2" fill="#5d4037" />
        <rect x="5" y="14" width="6" height="1" fill="#3e2723" />
      </template>
      <template v-else-if="level === 3">
        <!-- Lv3 矿洞学徒：铁盔 + 铁甲 + 手电 -->
        <rect x="4" y="1" width="8" height="1" fill="#bdbdbd" />
        <rect x="3" y="2" width="10" height="1" fill="#9e9e9e" />
        <rect x="7" y="1" width="2" height="1" fill="#ffd54f" />
        <rect x="4" y="3" width="8" height="2" fill="#ffe0b2" />
        <rect x="5" y="3" width="1" height="1" fill="#5d4037" />
        <rect x="10" y="3" width="1" height="1" fill="#5d4037" />
        <rect x="6" y="5" width="4" height="1" fill="#ffe0b2" />
        <rect x="3" y="6" width="10" height="4" fill="#78909c" />
        <rect x="6" y="7" width="1" height="1" fill="#26c6da" />
        <rect x="9" y="7" width="1" height="1" fill="#26c6da" />
        <rect x="2" y="8" width="1" height="3" fill="#ffd54f" />
        <rect x="3" y="10" width="10" height="2" fill="#546e7a" />
        <rect x="4" y="12" width="8" height="2" fill="#37474f" />
        <rect x="5" y="14" width="6" height="1" fill="#263238" />
      </template>
      <template v-else-if="level === 4">
        <!-- Lv4 铁匠大师：金盔 + 金甲 + 锤子 -->
        <rect x="4" y="1" width="8" height="1" fill="#ffd54f" />
        <rect x="3" y="2" width="10" height="1" fill="#ffb300" />
        <rect x="7" y="1" width="2" height="1" fill="#ff6f00" />
        <rect x="4" y="3" width="8" height="2" fill="#ffe0b2" />
        <rect x="5" y="3" width="1" height="1" fill="#5d4037" />
        <rect x="10" y="3" width="1" height="1" fill="#5d4037" />
        <rect x="6" y="5" width="4" height="1" fill="#ffe0b2" />
        <rect x="3" y="6" width="10" height="4" fill="#ffb300" />
        <rect x="6" y="7" width="1" height="1" fill="#e65100" />
        <rect x="9" y="7" width="1" height="1" fill="#e65100" />
        <rect x="1" y="7" width="2" height="1" fill="#8d6e63" />
        <rect x="2" y="8" width="1" height="3" fill="#5d4037" />
        <rect x="3" y="10" width="10" height="2" fill="#ff8f00" />
        <rect x="4" y="12" width="8" height="2" fill="#5d4037" />
        <rect x="5" y="14" width="6" height="1" fill="#3e2723" />
      </template>
      <template v-else-if="level === 5">
        <!-- Lv5 魔法师：紫色法袍 + 法杖 + 金色光圈 -->
        <rect x="5" y="0" width="6" height="1" fill="#ce93d8" />
        <rect x="4" y="1" width="8" height="1" fill="#ab47bc" />
        <rect x="7" y="0" width="2" height="1" fill="#fff" />
        <rect x="4" y="2" width="8" height="3" fill="#ffe0b2" />
        <rect x="5" y="3" width="1" height="1" fill="#4a148c" />
        <rect x="10" y="3" width="1" height="1" fill="#4a148c" />
        <rect x="6" y="5" width="4" height="1" fill="#ffe0b2" />
        <rect x="3" y="6" width="10" height="4" fill="#7b1fa2" />
        <rect x="6" y="7" width="1" height="1" fill="#e1bee7" />
        <rect x="9" y="7" width="1" height="1" fill="#e1bee7" />
        <rect x="13" y="4" width="1" height="8" fill="#ffd54f" />
        <rect x="12" y="3" width="3" height="1" fill="#ffd54f" />
        <rect x="3" y="10" width="10" height="2" fill="#6a1b9a" />
        <rect x="4" y="12" width="8" height="2" fill="#4a148c" />
        <rect x="5" y="14" width="6" height="1" fill="#311b92" />
      </template>
      <template v-else>
        <!-- Lv6 远古守护者：金甲 + 翅膀 + 王冠 -->
        <rect x="5" y="0" width="2" height="1" fill="#ffd54f" />
        <rect x="9" y="0" width="2" height="1" fill="#ffd54f" />
        <rect x="4" y="1" width="8" height="1" fill="#ffb300" />
        <rect x="7" y="0" width="2" height="1" fill="#ff6f00" />
        <rect x="4" y="2" width="8" height="3" fill="#ffe0b2" />
        <rect x="5" y="3" width="1" height="1" fill="#33691e" />
        <rect x="10" y="3" width="1" height="1" fill="#33691e" />
        <rect x="6" y="5" width="4" height="1" fill="#ffe0b2" />
        <!-- 翅膀 -->
        <rect x="1" y="6" width="2" height="1" fill="#fff9c4" />
        <rect x="13" y="6" width="2" height="1" fill="#fff9c4" />
        <rect x="3" y="6" width="10" height="4" fill="#ffd54f" />
        <rect x="0" y="7" width="3" height="1" fill="#fff" />
        <rect x="13" y="7" width="3" height="1" fill="#fff" />
        <rect x="6" y="7" width="1" height="1" fill="#e65100" />
        <rect x="9" y="7" width="1" height="1" fill="#e65100" />
        <rect x="3" y="10" width="10" height="2" fill="#ffb300" />
        <rect x="4" y="12" width="8" height="2" fill="#e65100" />
        <rect x="5" y="14" width="6" height="1" fill="#bf360c" />
      </template>
    </svg>

    <!-- 宝石图标 -->
    <svg v-else-if="type === 'gem'" :width="size" :height="size" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg" shape-rendering="crispEdges">
      <rect x="4" y="2" width="8" height="1" fill="#26c6da" />
      <rect x="3" y="3" width="10" height="1" fill="#4dd0e1" />
      <rect x="2" y="4" width="12" height="1" fill="#80deea" />
      <rect x="2" y="5" width="12" height="3" fill="#26c6da" />
      <rect x="3" y="5" width="2" height="2" fill="#b2ebf2" />
      <rect x="3" y="8" width="2" height="1" fill="#0097a7" />
      <rect x="5" y="8" width="2" height="1" fill="#26c6da" />
      <rect x="7" y="8" width="2" height="1" fill="#0097a7" />
      <rect x="9" y="8" width="2" height="1" fill="#26c6da" />
      <rect x="11" y="8" width="2" height="1" fill="#0097a7" />
      <rect x="4" y="9" width="8" height="1" fill="#0097a7" />
      <rect x="5" y="10" width="6" height="1" fill="#00838f" />
      <rect x="6" y="11" width="4" height="1" fill="#006064" />
      <rect x="7" y="12" width="2" height="1" fill="#004d40" />
    </svg>

    <!-- 徽章图标 -->
    <svg v-else-if="type === 'badge'" :width="size" :height="size" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg" shape-rendering="crispEdges">
      <template v-if="achCategory">
        <!-- 成就专属图标：按类别 + 段位配色 -->
        <!-- 外框 -->
        <rect x="2" y="2" width="12" height="12" :fill="tierDark" />
        <rect x="3" y="3" width="10" height="10" :fill="tierMain" />

        <template v-if="achCategory === 'study'">
          <!-- 学习：书本 -->
          <rect x="4" y="5" width="8" height="7" fill="#fff8e1" />
          <rect x="7" y="5" width="2" height="7" :fill="tierDark" />
          <rect x="5" y="6" width="2" height="1" :fill="tierLight" />
          <rect x="5" y="8" width="2" height="1" :fill="tierLight" />
          <rect x="9" y="6" width="2" height="1" :fill="tierLight" />
          <rect x="9" y="8" width="2" height="1" :fill="tierLight" />
        </template>
        <template v-else-if="achCategory === 'chore'">
          <!-- 家务：扫帚 -->
          <rect x="10" y="3" width="2" height="7" :fill="tierDark" />
          <rect x="9" y="3" width="4" height="1" :fill="tierLight" />
          <rect x="5" y="10" width="8" height="1" :fill="tierLight" />
          <rect x="4" y="11" width="10" height="1" :fill="tierMain" />
          <rect x="4" y="12" width="3" height="1" :fill="tierDark" />
          <rect x="8" y="12" width="3" height="1" :fill="tierDark" />
          <rect x="12" y="12" width="1" height="1" :fill="tierDark" />
        </template>
        <template v-else-if="achCategory === 'habit'">
          <!-- 习惯：闹钟 -->
          <rect x="5" y="4" width="2" height="1" :fill="tierDark" />
          <rect x="9" y="4" width="2" height="1" :fill="tierDark" />
          <rect x="4" y="5" width="8" height="6" :fill="tierMain" />
          <rect x="5" y="6" width="6" height="4" :fill="tierLight" />
          <rect x="8" y="7" width="1" height="2" :fill="tierDark" />
          <rect x="7" y="9" width="2" height="1" :fill="tierDark" />
          <rect x="7" y="11" width="2" height="1" :fill="tierDark" />
        </template>
        <template v-else-if="achCategory === 'score'">
          <!-- 积分：宝石 -->
          <rect x="3" y="5" width="10" height="1" :fill="tierLight" />
          <rect x="4" y="6" width="8" height="3" :fill="tierMain" />
          <rect x="5" y="9" width="6" height="1" :fill="tierMain" />
          <rect x="6" y="10" width="4" height="1" :fill="tierDark" />
          <rect x="7" y="11" width="2" height="1" :fill="tierDark" />
        </template>
        <template v-else-if="achCategory === 'exchange'">
          <!-- 兑换：礼物盒 -->
          <rect x="5" y="4" width="6" height="2" :fill="tierLight" />
          <rect x="4" y="6" width="8" height="7" :fill="tierMain" />
          <rect x="7" y="6" width="2" height="7" :fill="tierDark" />
          <rect x="6" y="4" width="1" height="2" :fill="tierDark" />
          <rect x="9" y="4" width="1" height="2" :fill="tierDark" />
        </template>
        <template v-else-if="achCategory === 'challenge'">
          <!-- 挑战：盾牌 -->
          <rect x="5" y="4" width="6" height="1" :fill="tierLight" />
          <rect x="4" y="5" width="8" height="2" :fill="tierMain" />
          <rect x="4" y="7" width="8" height="4" :fill="tierMain" />
          <rect x="5" y="11" width="6" height="1" :fill="tierDark" />
          <rect x="6" y="12" width="4" height="1" :fill="tierDark" />
        </template>
        <template v-else-if="achCategory === 'checkin'">
          <!-- 打卡：日历 -->
          <rect x="5" y="4" width="2" height="1" :fill="tierDark" />
          <rect x="9" y="4" width="2" height="1" :fill="tierDark" />
          <rect x="3" y="5" width="10" height="7" :fill="tierMain" />
          <rect x="4" y="6" width="8" height="5" :fill="tierLight" />
          <rect x="5" y="8" width="1" height="2" :fill="tierDark" />
          <rect x="10" y="8" width="1" height="2" :fill="tierDark" />
        </template>
        <template v-else-if="achCategory === 'goal'">
          <!-- 目标：旗帜 -->
          <rect x="7" y="4" width="1" height="9" :fill="tierDark" />
          <rect x="8" y="4" width="5" height="2" :fill="tierMain" />
          <rect x="8" y="6" width="4" height="2" :fill="tierLight" />
        </template>
        <template v-else-if="achCategory === 'bank'">
          <!-- 银行：储蓄罐 -->
          <rect x="4" y="4" width="1" height="1" :fill="tierLight" />
          <rect x="5" y="3" width="6" height="1" :fill="tierLight" />
          <rect x="11" y="4" width="1" height="1" :fill="tierLight" />
          <rect x="5" y="5" width="7" height="7" :fill="tierMain" />
          <rect x="3" y="6" width="3" height="1" :fill="tierMain" />
          <rect x="3" y="7" width="3" height="3" :fill="tierMain" />
          <rect x="6" y="6" width="1" height="1" :fill="tierDark" />
          <rect x="12" y="12" width="1" height="1" :fill="tierDark" />
          <rect x="11" y="12" width="1" height="1" :fill="tierDark" />
        </template>
        <template v-else>
          <!-- 兜底：奖牌 -->
          <rect x="6" y="4" width="4" height="2" :fill="tierLight" />
          <rect x="5" y="6" width="6" height="5" :fill="tierMain" />
          <rect x="6" y="11" width="4" height="1" :fill="tierDark" />
          <rect x="7" y="7" width="2" height="2" :fill="tierLight" />
        </template>
      </template>
      <template v-else-if="rarity === 'common'">
        <!-- 普通：金色圆形 -->
        <rect x="3" y="3" width="10" height="10" fill="#ffd54f" rx="5" />
        <rect x="5" y="5" width="6" height="6" fill="#ffb300" rx="3" />
        <rect x="6" y="6" width="2" height="2" fill="#fff9c4" />
      </template>
      <template v-else-if="rarity === 'rare'">
        <!-- 稀有：橙色六角星 -->
        <rect x="7" y="2" width="2" height="1" fill="#ff9800" />
        <rect x="5" y="3" width="6" height="1" fill="#f57c00" />
        <rect x="3" y="4" width="10" height="3" fill="#ff9800" />
        <rect x="2" y="5" width="12" height="2" fill="#ffa726" />
        <rect x="3" y="8" width="10" height="1" fill="#f57c00" />
        <rect x="4" y="9" width="2" height="2" fill="#ef6c00" />
        <rect x="10" y="9" width="2" height="2" fill="#ef6c00" />
        <rect x="5" y="11" width="2" height="2" fill="#e65100" />
        <rect x="9" y="11" width="2" height="2" fill="#e65100" />
        <rect x="7" y="13" width="2" height="1" fill="#bf360c" />
        <rect x="6" y="5" width="2" height="2" fill="#ffe0b2" />
      </template>
      <template v-else-if="rarity === 'epic'">
        <!-- 史诗：紫色菱形 -->
        <rect x="7" y="1" width="2" height="1" fill="#ce93d8" />
        <rect x="6" y="2" width="4" height="1" fill="#ab47bc" />
        <rect x="5" y="3" width="6" height="1" fill="#9c27b0" />
        <rect x="4" y="4" width="8" height="1" fill="#8e24aa" />
        <rect x="3" y="5" width="10" height="2" fill="#7b1fa2" />
        <rect x="4" y="7" width="8" height="1" fill="#8e24aa" />
        <rect x="5" y="8" width="6" height="1" fill="#9c27b0" />
        <rect x="6" y="9" width="4" height="1" fill="#ab47bc" />
        <rect x="7" y="10" width="2" height="1" fill="#ce93d8" />
        <rect x="6" y="5" width="2" height="2" fill="#e1bee7" />
      </template>
      <template v-else>
        <!-- 传说：红色王冠+火焰 -->
        <rect x="5" y="2" width="2" height="1" fill="#ffd54f" />
        <rect x="9" y="2" width="2" height="1" fill="#ffd54f" />
        <rect x="4" y="3" width="8" height="1" fill="#ffb300" />
        <rect x="7" y="2" width="2" height="1" fill="#ff6f00" />
        <rect x="3" y="4" width="10" height="3" fill="#ef5350" />
        <rect x="2" y="5" width="12" height="2" fill="#e53935" />
        <rect x="3" y="7" width="10" height="1" fill="#c62828" />
        <rect x="4" y="8" width="8" height="2" fill="#b71c1c" />
        <rect x="5" y="10" width="6" height="2" fill="#d32f2f" />
        <rect x="6" y="12" width="4" height="1" fill="#f44336" />
        <rect x="7" y="13" width="2" height="1" fill="#ff5252" />
        <rect x="6" y="4" width="2" height="2" fill="#ffcdd2" />
      </template>
    </svg>

    <!-- 任务类型图标 -->
    <svg v-else-if="type === 'task'" :width="size" :height="size" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg" shape-rendering="crispEdges">
      <template v-if="taskType === '学习'">
        <!-- 书本 -->
        <rect x="2" y="3" width="12" height="10" fill="#43a047" />
        <rect x="3" y="4" width="10" height="8" fill="#e8f5e9" />
        <rect x="8" y="4" width="1" height="8" fill="#66bb6a" />
        <rect x="4" y="5" width="3" height="1" fill="#81c784" />
        <rect x="4" y="6" width="3" height="1" fill="#81c784" />
        <rect x="4" y="7" width="3" height="1" fill="#81c784" />
        <rect x="9" y="5" width="3" height="1" fill="#81c784" />
        <rect x="9" y="6" width="3" height="1" fill="#81c784" />
        <rect x="9" y="7" width="3" height="1" fill="#81c784" />
      </template>
      <template v-else-if="taskType === '家务'">
        <!-- 扫帚 -->
        <rect x="9" y="1" width="1" height="8" fill="#8d6e63" />
        <rect x="8" y="1" width="3" height="1" fill="#5d4037" />
        <rect x="5" y="9" width="8" height="1" fill="#ffb300" />
        <rect x="4" y="10" width="10" height="1" fill="#ff8f00" />
        <rect x="4" y="11" width="3" height="3" fill="#ff8f00" />
        <rect x="7" y="11" width="3" height="3" fill="#ff8f00" />
        <rect x="10" y="11" width="3" height="3" fill="#ff8f00" />
        <rect x="4" y="14" width="2" height="1" fill="#e65100" />
        <rect x="7" y="14" width="2" height="1" fill="#e65100" />
        <rect x="10" y="14" width="2" height="1" fill="#e65100" />
      </template>
      <template v-else-if="taskType === '习惯'">
        <!-- 闹钟 -->
        <rect x="4" y="2" width="2" height="1" fill="#5d4037" />
        <rect x="10" y="2" width="2" height="1" fill="#5d4037" />
        <rect x="3" y="3" width="10" height="9" fill="#ffd54f" />
        <rect x="4" y="4" width="8" height="7" fill="#fff8e1" />
        <rect x="7" y="5" width="1" height="4" fill="#e65100" />
        <rect x="7" y="8" width="3" height="1" fill="#e65100" />
        <rect x="6" y="12" width="2" height="1" fill="#5d4037" />
        <rect x="8" y="12" width="2" height="1" fill="#5d4037" />
      </template>
      <template v-else-if="taskType === '品德'">
        <!-- 爱心 -->
        <rect x="5" y="3" width="2" height="1" fill="#e53935" />
        <rect x="9" y="3" width="2" height="1" fill="#e53935" />
        <rect x="3" y="4" width="4" height="1" fill="#ef5350" />
        <rect x="9" y="4" width="4" height="1" fill="#ef5350" />
        <rect x="2" y="5" width="12" height="3" fill="#e53935" />
        <rect x="3" y="8" width="10" height="1" fill="#c62828" />
        <rect x="4" y="9" width="8" height="1" fill="#c62828" />
        <rect x="5" y="10" width="6" height="1" fill="#b71c1c" />
        <rect x="6" y="11" width="4" height="1" fill="#b71c1c" />
        <rect x="7" y="12" width="2" height="1" fill="#d32f2f" />
      </template>
      <template v-else>
        <!-- 临时：星星 -->
        <rect x="7" y="1" width="2" height="2" fill="#ffd54f" />
        <rect x="6" y="3" width="4" height="1" fill="#ffb300" />
        <rect x="1" y="4" width="14" height="2" fill="#ffd54f" />
        <rect x="3" y="6" width="3" height="1" fill="#ffb300" />
        <rect x="10" y="6" width="3" height="1" fill="#ffb300" />
        <rect x="4" y="7" width="3" height="1" fill="#ff8f00" />
        <rect x="9" y="7" width="3" height="1" fill="#ff8f00" />
        <rect x="5" y="8" width="2" height="2" fill="#e65100" />
        <rect x="9" y="8" width="2" height="2" fill="#e65100" />
        <rect x="6" y="10" width="4" height="1" fill="#bf360c" />
        <rect x="7" y="11" width="2" height="2" fill="#bf360c" />
      </template>
    </svg>

    <!-- 奖励图标 -->
    <svg v-else-if="type === 'reward'" :width="size" :height="size" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg" shape-rendering="crispEdges">
      <template v-if="rewardKey === 'tv'">
        <!-- 电视 -->
        <rect x="2" y="3" width="12" height="9" fill="#37474f" />
        <rect x="3" y="4" width="10" height="7" fill="#26c6da" />
        <rect x="4" y="5" width="8" height="5" fill="#4dd0e1" />
        <rect x="5" y="5" width="2" height="1" fill="#80deea" />
        <rect x="12" y="10" width="1" height="1" fill="#ffd54f" />
        <rect x="4" y="12" width="8" height="1" fill="#5d4037" />
        <rect x="5" y="13" width="2" height="1" fill="#5d4037" />
        <rect x="9" y="13" width="2" height="1" fill="#5d4037" />
      </template>
      <template v-else-if="rewardKey === 'tablet'">
        <!-- 平板 -->
        <rect x="3" y="2" width="10" height="12" fill="#37474f" />
        <rect x="4" y="3" width="8" height="9" fill="#26c6da" />
        <rect x="5" y="4" width="6" height="7" fill="#80deea" />
        <rect x="6" y="4" width="2" height="1" fill="#b2ebf2" />
        <rect x="7" y="12" width="2" height="1" fill="#5d4037" />
      </template>
      <template v-else-if="rewardKey === 'snack'">
        <!-- 饼干 -->
        <rect x="4" y="3" width="8" height="1" fill="#8d6e63" />
        <rect x="3" y="4" width="10" height="1" fill="#a1887f" />
        <rect x="2" y="5" width="12" height="5" fill="#8d6e63" />
        <rect x="3" y="10" width="10" height="1" fill="#a1887f" />
        <rect x="4" y="11" width="8" height="1" fill="#6d4c41" />
        <rect x="5" y="6" width="1" height="1" fill="#5d4037" />
        <rect x="9" y="7" width="1" height="1" fill="#5d4037" />
        <rect x="7" y="8" width="1" height="1" fill="#5d4037" />
        <rect x="10" y="9" width="1" height="1" fill="#5d4037" />
        <rect x="6" y="9" width="1" height="1" fill="#5d4037" />
      </template>
      <template v-else>
        <!-- 礼物盒 -->
        <rect x="3" y="5" width="10" height="9" fill="#43a047" />
        <rect x="3" y="5" width="10" height="2" fill="#66bb6a" />
        <rect x="7" y="5" width="2" height="9" fill="#e53935" />
        <rect x="5" y="3" width="6" height="2" fill="#ef5350" />
        <rect x="6" y="2" width="2" height="1" fill="#e53935" />
        <rect x="8" y="2" width="2" height="1" fill="#e53935" />
        <rect x="7" y="5" width="2" height="2" fill="#ffd54f" />
      </template>
    </svg>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  type: 'avatar' | 'gem' | 'badge' | 'task' | 'reward'
  size?: number
  level?: number
  rarity?: string
  taskType?: string
  rewardKey?: string
  code?: string
  tier?: number
}>(), {
  size: 32,
  level: 1,
  rarity: 'common',
  taskType: '学习',
  rewardKey: 'gift',
  code: '',
  tier: 1,
})

const level = computed(() => props.level)

// 从成就 code 解析类别（前缀，如 study_streak -> study）
const achCategory = computed(() => {
  if (!props.code) return ''
  const first = props.code.split('_')[0]
  const map: Record<string, string> = {
    study: 'study',
    homework: 'study',
    reading: 'study',
    chore: 'chore',
    clean: 'chore',
    helper: 'chore',
    habit: 'habit',
    early: 'habit',
    sleep: 'habit',
    score: 'score',
    first: 'score',
    exchange: 'exchange',
    challenge: 'challenge',
    checkin: 'checkin',
    goal: 'goal',
    saver: 'bank',
    wealth: 'bank',
  }
  return map[first] || ''
})

// 段位配色
const TIER_COLORS: Record<number, { main: string; dark: string; light: string }> = {
  1: { main: '#cd7f32', dark: '#8d5a23', light: '#e8b872' }, // 青铜
  2: { main: '#c0c0c0', dark: '#8a8a8a', light: '#f0f0f0' }, // 白银
  3: { main: '#ffd700', dark: '#c9a800', light: '#fff4a3' }, // 黄金
  4: { main: '#b9f2ff', dark: '#5ecbe0', light: '#e5fcff' }, // 钻石
}
const tierColors = computed(() => TIER_COLORS[props.tier] || TIER_COLORS[1])
const tierMain = computed(() => tierColors.value.main)
const tierDark = computed(() => tierColors.value.dark)
const tierLight = computed(() => tierColors.value.light)
</script>

<style scoped>
.pixel-icon {
  display: inline-flex;
  vertical-align: middle;
}
</style>
