<template>
  <div
    class="dip-wrap"
    :class="{
      'dip-flip': placement === 'left',
      'dip-wrap--center': placement === 'center'
    }"
    @mouseenter="$emit('popoverEnter')"
    @mouseleave="$emit('popoverLeave')"
  >
    <div v-if="placement !== 'center'" class="dip-connector" aria-hidden="true" />
    <div class="dip-card" :class="`dip--${dominantUrgency}`">
      <div
        v-for="(issue, i) in issues"
        :key="issue.id"
        class="dip-issue-block"
        :class="{ 'dip-issue-block--sep': i > 0 }"
      >
        <div class="dip-header">
          <span class="dip-order">{{ i + 1 }}</span>
          <span class="dip-badge" :class="`dip-badge--${getIssueUrgency(issue)}`">{{ urgencyLabel(issue) }}</span>
          <span v-if="issue.category" class="dip-cat">{{ issue.category }}</span>
        </div>
        <div class="dip-title">{{ issue.title || '未命名问题' }}</div>
        <div class="dip-body">
          <p v-if="issue.desc" class="dip-row">
            <span class="dip-lbl">实测</span>
            <span class="dip-val">{{ issue.desc }}</span>
          </p>
          <p v-if="issue.suggestion" class="dip-row">
            <span class="dip-lbl">建议</span>
            <span class="dip-val">{{ issue.suggestion }}</span>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { getIssueUrgency } from '../utils/issueUrgency'

const props = defineProps({
  issues: { type: Array, required: true },
  /** right / left / center（居中时不显示连接线） */
  placement: { type: String, default: 'right' }
})

defineEmits(['popoverEnter', 'popoverLeave'])

function urgencyLabel(issue) {
  const u = getIssueUrgency(issue)
  if (u === 'high') return '高'
  if (u === 'medium') return '中'
  return '低'
}

const dominantUrgency = computed(() => {
  const order = { high: 3, medium: 2, low: 1 }
  let best = 'low'
  let max = 0
  for (const issue of props.issues) {
    const u = getIssueUrgency(issue)
    if (order[u] > max) {
      max = order[u]
      best = u
    }
  }
  return best
})
</script>

<style scoped>
.dip-wrap {
  position: relative;
  pointer-events: auto;
  width: 100%;
  max-width: 300px;
}

.dip-wrap--center .dip-connector {
  display: none;
}

.dip-connector {
  position: absolute;
  width: 10px;
  height: 2px;
  left: -10px;
  top: 14px;
  background: linear-gradient(90deg, rgba(26, 106, 255, 0.35), rgba(255, 255, 255, 0.2));
  border-radius: 1px;
}

.dip-flip .dip-connector {
  left: auto;
  right: -10px;
  background: linear-gradient(270deg, rgba(26, 106, 255, 0.35), rgba(255, 255, 255, 0.2));
}

.dip-card {
  background: rgba(22, 24, 38, 0.96);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  padding: 10px 12px 12px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(0, 0, 0, 0.12);
  backdrop-filter: blur(10px);
  max-height: min(360px, 70vh);
  overflow-y: auto;
  box-sizing: border-box;
}

.dip-issue-block--sep {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.dip-header {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.dip-order {
  flex-shrink: 0;
  min-width: 22px;
  height: 22px;
  padding: 0 6px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.14);
  color: #fff;
  font-size: 0.7rem;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.dip-badge {
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.02em;
  padding: 2px 7px;
  border-radius: 4px;
  color: #fff;
}

.dip-badge--high {
  background: #dc2626;
  box-shadow: 0 0 0 1px rgba(254, 202, 202, 0.35);
}

.dip-badge--medium {
  background: #d97706;
  box-shadow: 0 0 0 1px rgba(253, 230, 138, 0.35);
}

.dip-badge--low {
  background: #2563eb;
  box-shadow: 0 0 0 1px rgba(191, 219, 254, 0.35);
}

.dip--high .dip-order {
  box-shadow: 0 0 0 1px rgba(254, 202, 202, 0.25);
}

.dip--medium .dip-order {
  box-shadow: 0 0 0 1px rgba(253, 230, 138, 0.25);
}

.dip--low .dip-order {
  box-shadow: 0 0 0 1px rgba(191, 219, 254, 0.25);
}

.dip-cat {
  font-size: 0.65rem;
  color: #9ca3af;
  font-weight: 600;
}

.dip-title {
  font-size: 0.82rem;
  font-weight: 700;
  color: #f9fafb;
  line-height: 1.35;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.dip-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dip-row {
  margin: 0;
  font-size: 0.72rem;
  line-height: 1.45;
  color: #e5e7eb;
}

.dip-lbl {
  display: block;
  font-size: 0.62rem;
  font-weight: 700;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 3px;
}

.dip-val {
  display: block;
  word-break: break-word;
}
</style>
