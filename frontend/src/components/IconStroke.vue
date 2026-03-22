<template>
  <svg
    class="icon-stroke"
    :class="[`icon-stroke--${name}`, sizeClass]"
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
    :stroke-width="strokeWeight"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <!-- 走查模式：基准值 / 规范列表 -->
    <g v-if="name === 'baseline'">
      <path d="M9 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2" />
      <path d="M9 9h6M9 13h6M9 17h4" />
    </g>
    <!-- 走查模式：组件 2x2 栅格 -->
    <g v-else-if="name === 'component'">
      <rect x="3" y="3" width="7" height="7" rx="1" />
      <rect x="14" y="3" width="7" height="7" rx="1" />
      <rect x="3" y="14" width="7" height="7" rx="1" />
      <rect x="14" y="14" width="7" height="7" rx="1" />
    </g>
    <!-- 走查模式：设计稿 / 画框 -->
    <g v-else-if="name === 'design'">
      <rect x="3" y="3" width="18" height="18" rx="2" />
      <path d="M3 16l5-5 4 4 5-6 5 5" />
      <circle cx="8.5" cy="8.5" r="1.5" />
    </g>
    <path v-else-if="name === 'link'" d="M10 13a5 5 0 0 1 0-7l1-1a5 5 0 0 1 7 7l-1 1M14 11a5 5 0 0 1 0 7l-1 1a5 5 0 0 1-7-7l1-1" />
    <!-- 线性闪电：path 不填充，仅描边（粗细由 stroke-width 控制，默认 2） -->
    <path v-else-if="name === 'bolt'" fill="none" d="M13 2L4 14h7l-1 8 9-12h-7l1-8z" />
    <g v-else-if="name === 'clock'">
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3 2" />
    </g>
    <g v-else-if="name === 'inbox'">
      <path d="M4 4h16v4H4V4z" />
      <path d="M4 8v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-2-2H6l-2 2z" />
    </g>
    <g v-else-if="name === 'search'">
      <circle cx="11" cy="11" r="6" />
      <path d="m20 20-3-3" />
    </g>
    <g v-else-if="name === 'trash'">
      <path d="M4 8h16" />
      <rect x="9.5" y="4" width="5" height="3" rx="0.5" />
      <path d="M8 9.5h8v11a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2v-11z" />
      <path d="M10.5 13v6M13.5 13v6" />
    </g>
    <path v-else-if="name === 'user'" d="M20 21a8 8 0 0 0-16 0M12 11a4 4 0 1 0-4-4 4 4 0 0 0 4 4z" />
    <g v-else-if="name === 'lock'">
      <rect x="5" y="11" width="14" height="10" rx="2" />
      <path d="M8 11V8a4 4 0 0 1 8 0v3" />
    </g>
    <path v-else-if="name === 'logout'" d="M10 17H6a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h4M14 8l4 4-4 4M19 12H9" />
    <path v-else-if="name === 'check'" d="M5 13l4 4L19 7" />
    <path v-else-if="name === 'chevron-down'" d="M6 9l6 6 6-6" />
    <path v-else-if="name === 'sparkle'" d="M12 3l1.2 3.6L17 8l-3.8 1.2L12 13l-1.2-3.8L7 8l3.8-1.4L12 3z" />
    <!-- 基准值区块：调色板 / 栅格 / 动效 / 排版 / 图层 -->
    <g v-else-if="name === 'palette'">
      <circle cx="8" cy="9" r="3" />
      <circle cx="16" cy="9" r="3" />
      <circle cx="12" cy="15" r="3" />
    </g>
    <g v-else-if="name === 'layout-grid'">
      <rect x="4" y="4" width="6" height="6" rx="1" />
      <rect x="14" y="4" width="6" height="6" rx="1" />
      <rect x="4" y="14" width="6" height="6" rx="1" />
      <rect x="14" y="14" width="6" height="6" rx="1" />
    </g>
    <g v-else-if="name === 'film'">
      <rect x="3" y="7" width="18" height="10" rx="2" />
      <path d="M3 10h2M3 14h2M21 10h2M21 14h2" />
    </g>
    <g v-else-if="name === 'typography'">
      <path d="M5 7h14M5 12h10M5 17h14" />
      <path d="M17 7v10" />
    </g>
    <g v-else-if="name === 'layers'">
      <path d="M12 4L4 8l8 4 8-4-8-4z" />
      <path d="M4 13l8 4 8-4M4 18l8 4 8-4" />
    </g>
    <g v-else-if="name === 'cursor'">
      <path d="M3 3l7.07 16.97 2.51-7.55 7.55-2.51L3 3z" />
    </g>
    <g v-else-if="name === 'accessibility'">
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5M9 12h6M10 17h4" />
    </g>
    <!-- 设计稿模式区块标题 -->
    <g v-else-if="name === 'ruler'">
      <path d="M4 20L20 4" />
      <path d="M8 3h3v3M3 8V5h3" />
    </g>
    <g v-else-if="name === 'chip-ai'">
      <rect x="4" y="7" width="16" height="10" rx="2" />
      <path d="M9 12h6M12 9v6" />
      <circle cx="17" cy="9" r="1.2" />
    </g>
    <g v-else-if="name === 'crosshair'">
      <circle cx="12" cy="12" r="3" />
      <path d="M12 5v3M12 16v3M5 12h3M16 12h3" />
    </g>
    <g v-else-if="name === 'report'">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
      <polyline points="10 9 9 9 8 9" />
    </g>
  </svg>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  /** baseline | component | design | palette | layout-grid | film | typography | layers | cursor | accessibility | ruler | chip-ai | crosshair | link | bolt | clock | inbox | search | trash | user | lock | logout | sparkle */
  name: { type: String, required: true },
  /** sm 16px, md 24px, lg 32px */
  size: { type: String, default: 'md' },
  /** 描边粗细（px），如删除按钮可用 1.2 */
  strokeWeight: { type: String, default: '2' },
})

const sizeClass = computed(() => {
  const map = { sm: 'icon-stroke--sm', md: 'icon-stroke--md', lg: 'icon-stroke--lg' }
  return map[props.size] || map.md
})
</script>

<style scoped>
.icon-stroke {
  display: inline-block;
  vertical-align: middle;
  flex-shrink: 0;
  color: inherit;
}
/* 全局线性图标统一视觉尺寸（sm/md/lg 一致） */
.icon-stroke--sm,
.icon-stroke--md,
.icon-stroke--lg { width: 20px; height: 20px; }
</style>
