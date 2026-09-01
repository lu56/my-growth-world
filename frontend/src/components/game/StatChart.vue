<template>
  <!-- 折线图 -->
  <svg v-if="type === 'line'" :viewBox="`0 0 ${width} ${height}`" class="w-full" :style="{ maxWidth: width + 'px' }">
    <!-- 网格线 -->
    <line v-for="i in 4" :key="'grid' + i" :x1="padL" :x2="width - padR" :y1="padT + (i - 1) * plotH / 4" :y2="padT + (i - 1) * plotH / 4" stroke="#e0d6c0" stroke-width="1" stroke-dasharray="3,3" />
    <!-- 面积渐变 -->
    <defs>
      <linearGradient :id="'area-' + uid" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="rgba(13,148,136,0.35)" />
        <stop offset="100%" stop-color="rgba(13,148,136,0.02)" />
      </linearGradient>
    </defs>
    <!-- 面积填充 -->
    <path v-if="linePoints.length > 1" :d="areaPath" :fill="'url(#area-' + uid + ')'" />
    <!-- 折线 -->
    <path v-if="linePoints.length > 1" :d="linePath" fill="none" stroke="#0d9488" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
    <!-- 数据点 -->
    <g v-for="(p, i) in linePoints" :key="'pt' + i">
      <circle :cx="p.x" :cy="p.y" r="3" fill="#fff" stroke="#0d9488" stroke-width="2" />
    </g>
    <!-- X轴标签 -->
    <g v-for="(d, i) in data" :key="'lbl' + i">
      <text v-if="data && i % Math.max(1, Math.floor(data.length / 7)) === 0" :x="linePoints[i]?.x" :y="height - 4" font-size="9" fill="#a16207" text-anchor="middle">{{ d.label }}</text>
    </g>
  </svg>

  <!-- 环形图 -->
  <svg v-else-if="type === 'donut'" :viewBox="`0 0 ${donutSize} ${donutSize}`" :style="{ width: donutSize + 'px', height: donutSize + 'px' }">
    <g :transform="`translate(${donutSize / 2}, ${donutSize / 2})`">
      <!-- 扇形 -->
      <path
        v-for="(seg, i) in donutSegments"
        :key="'seg' + i"
        :d="seg.path"
        :fill="seg.color"
        :stroke="'#fff'"
        :stroke-width="2"
      />
      <!-- 中心文字 -->
      <text x="0" y="-4" font-size="16" font-weight="bold" fill="#78350f" text-anchor="middle">{{ centerLabel }}</text>
      <text x="0" y="14" font-size="11" fill="#a16207" text-anchor="middle">{{ centerSubLabel }}</text>
    </g>
  </svg>

  <!-- 进度环 -->
  <svg v-else-if="type === 'ring'" :viewBox="`0 0 ${ringSize} ${ringSize}`" :style="{ width: ringSize + 'px', height: ringSize + 'px' }">
    <g :transform="`translate(${ringSize / 2}, ${ringSize / 2})`">
      <!-- 背景环 -->
      <circle :r="ringRadius" fill="none" stroke="#e0d6c0" :stroke-width="ringStroke" />
      <!-- 进度环 -->
      <circle
        :r="ringRadius"
        fill="none"
        :stroke="ringColor"
        :stroke-width="ringStroke"
        stroke-linecap="round"
        :stroke-dasharray="ringCircumference"
        :stroke-dashoffset="ringDashOffset"
        :transform="`rotate(-90)`"
        style="transition: stroke-dashoffset 0.6s ease"
      />
      <!-- 中心文字 -->
      <text x="0" y="-2" font-size="20" font-weight="bold" :fill="ringColor" text-anchor="middle">{{ ringPercent }}%</text>
      <text x="0" y="16" font-size="11" fill="#a16207" text-anchor="middle">{{ ringSubLabel }}</text>
    </g>
  </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  type: 'line' | 'donut' | 'ring'
  /** 折线图数据 */
  data?: { label: string; value: number }[]
  /** 环形图数据 */
  segments?: { label: string; value: number; color?: string }[]
  /** 进度环 0~1 */
  ratio?: number
  /** 中心主标签 */
  centerLabel?: string
  /** 中心副标签 */
  centerSubLabel?: string
  /** 进度环副标签 */
  ringSubLabel?: string
  /** 进度环颜色 */
  ringColor?: string
}>(), {
  ringColor: '#7c4dff',
  ringSubLabel: '完成率',
})

const uid = Math.random().toString(36).slice(2, 8)

// ---- 折线图参数 ----
const width = 320
const height = 140
const padL = 8
const padR = 8
const padT = 8
const plotW = width - padL - padR
const plotH = height - padT - 24

const maxValue = computed(() => {
  const vals = props.data?.map((d) => d.value) || []
  return Math.max(...vals, 1)
})

const linePoints = computed(() => {
  const d = props.data || []
  if (d.length === 0) return []
  const step = d.length > 1 ? plotW / (d.length - 1) : 0
  return d.map((item, i) => ({
    x: padL + i * step,
    y: padT + plotH - (item.value / maxValue.value) * plotH,
  }))
})

const linePath = computed(() => {
  const pts = linePoints.value
  if (pts.length === 0) return ''
  return pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
})

const areaPath = computed(() => {
  const pts = linePoints.value
  if (pts.length < 2) return ''
  const ptsStr = pts.map((p) => `L ${p.x} ${p.y}`).join(' ')
  return `M ${pts[0].x} ${padT + plotH} ${ptsStr} L ${pts[pts.length - 1].x} ${padT + plotH} Z`
})

// ---- 环形图参数 ----
const donutSize = 140
const donutRadius = 52
const donutStroke = 22

const DEFAULT_COLORS = ['#0d9488', '#f59e0b', '#7c4dff', '#ef4444', '#3b82f6', '#84cc16']

const donutSegments = computed(() => {
  const segs = props.segments || []
  const total = segs.reduce((s, x) => s + x.value, 0)
  if (total === 0) return []
  let acc = 0
  return segs.map((s, i) => {
    const startAngle = (acc / total) * Math.PI * 2 - Math.PI / 2
    acc += s.value
    const endAngle = (acc / total) * Math.PI * 2 - Math.PI / 2
    const x1 = Math.cos(startAngle) * donutRadius
    const y1 = Math.sin(startAngle) * donutRadius
    const x2 = Math.cos(endAngle) * donutRadius
    const y2 = Math.sin(endAngle) * donutRadius
    const largeArc = endAngle - startAngle > Math.PI ? 1 : 0
    return {
      path: `M ${x1} ${y1} A ${donutRadius} ${donutRadius} 0 ${largeArc} 1 ${x2} ${y2} L 0 0 Z`,
      color: s.color || DEFAULT_COLORS[i % DEFAULT_COLORS.length],
      label: s.label,
      value: s.value,
    }
  })
})

// ---- 进度环参数 ----
const ringSize = 120
const ringRadius = 46
const ringStroke = 10
const ringCircumference = 2 * Math.PI * ringRadius
const ringPercent = computed(() => Math.round((props.ratio || 0) * 100))
const ringDashOffset = computed(() => ringCircumference * (1 - (props.ratio || 0)))
</script>
