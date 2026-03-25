<template>
  <div class="dashboard-layout" v-if="reportData">
    <AppNavbar variant="breadcrumb">
      <template #actions>
        <button
          v-if="showGenerateReportBtn"
          class="btn btn-primary"
          style="margin-right:24px;"
          @click="goTo('/report')"
        ><IconStroke name="report" size="sm" stroke-weight="2" /> 生成详细报告</button>
      </template>
    </AppNavbar>

    <!-- 紧凑锚点气泡：弹窗层 pointer-events:auto + 最高 z-index，避免命中穿透到下方标注框 -->
    <Teleport to="body">
      <div
        ref="popoverLayerRef"
        v-show="hoveredIssues.length > 0"
        class="issue-popover-layer"
        :class="{ 'is-visible': hoveredIssues.length > 0 }"
        :style="popoverLayerStyle"
      >
        <DashboardIssuePopover
          v-if="hoveredIssues.length > 0"
          :issues="hoveredIssues"
          :placement="popoverPlacement"
          @popover-enter="onPopoverEnter"
          @popover-leave="onPopoverLeave"
        />
      </div>
    </Teleport>

    <!-- 文本省略号提示：Teleport 到 body，避免被侧栏裁切/遮挡 -->
    <Teleport to="body">
      <div v-show="textTip.visible" class="dash-text-tip" :style="textTip.style" aria-hidden="true">
        {{ textTip.text }}
      </div>
    </Teleport>

    <div class="dashboard-main">
      <div class="canvas-area">
        <div class="canvas-header">
          <div class="canvas-header-title">👁 页面实时预览 (重叠时优先识别较小框，悬停查看详情)</div>
        </div>

        <div ref="canvasViewportRef" class="canvas-viewport" @scroll.passive="schedulePopoverPosition">
          <div ref="mockDeviceRef" class="mock-device" :style="{ transform: `scale(${zoom / 100})` }">
            <img v-if="reportData.screenshot" :src="'data:image/png;base64,' + reportData.screenshot" class="actual-img" />
            <div v-else class="actual-img-placeholder">📸 后端未返回截图</div>

            <template v-if="issueMarkers.length > 0">
              <div
                v-for="(marker, idx) in issueMarkers"
                :key="marker.issue.id"
                class="annotation-box"
                :class="[`ann-${marker.urgency}`, { 'is-popover-active': hoveredRectKey && markerRectKey(marker) === hoveredRectKey }]"
                :data-issue-id="getMarkerDataId(marker, idx)"
                :style="{
                  top: marker.rect.top + 'px',
                  left: marker.rect.left + 'px',
                  width: marker.rect.width + 'px',
                  height: marker.rect.height + 'px',
                  zIndex: 10 + idx
                }"
              />
            </template>
          </div>
        </div>

        <div class="zoom-controls">
          <button @click="zoom -= 10">−</button><span>{{ zoom }}%</span><button @click="zoom += 10">+</button>
        </div>
      </div>

      <div class="sidebar">
        <div class="sidebar-header">
          <div class="sidebar-header-title">属性审计对比列表</div>
          <div class="sidebar-header-hint">
            <span>检测到 <strong style="color:#ef4444;">{{ reportData.issueCount || 0 }}</strong> 个不符合规范的属性</span>
            <FilterSelect
              v-model="selectedCategory"
              :options="categoryOptions"
              menu-label="问题分类"
              class="dash-category-select"
            />
          </div>
        </div>

        <div class="sidebar-body">
          <table class="audit-table">
            <colgroup>
              <col class="col-idx" />
              <col />
              <col />
              <col />
              <col class="col-status" />
            </colgroup>
            <thead>
              <tr>
                <th class="th-idx">序号</th>
                <th>审计项</th>
                <th class="th-actual">实测值</th>
                <th class="th-standard">标准值/建议</th>
                <th class="th-status">状态</th>
              </tr>
            </thead>
            <tbody>
              <template v-if="reportData.issues && reportData.issues.length > 0">
                <tr v-for="(issue, rowIdx) in pagedTableIssues" :key="issue.id" class="data-row">
                  <td class="row-idx">{{ (tableCurrentPage - 1) * tablePageSize + rowIdx + 1 }}</td>
                  <td class="attr-name">{{ issue.title || '未知' }}</td>
                  <td class="actual-val" :class="`val-${getIssueUrgency(issue)}`">
                    <div class="tip-anchor" :data-tip="extractValue(issue.desc, true)">
                      <div class="cell-main tip-text">{{ extractValue(issue.desc, true) }}</div>
                    </div>
                  </td>
                  <td class="standard-val">
                    <div
                      class="tip-anchor"
                      @mouseenter="onTextTipEnter($event, issue.suggestion || '请参考规范')"
                      @mousemove="onTextTipMove"
                      @mouseleave="onTextTipLeave"
                      @focusin="onTextTipEnter($event, issue.suggestion || '请参考规范')"
                      @focusout="onTextTipLeave"
                      tabindex="0"
                    >
                      <div class="fix-link tip-text">{{ issue.suggestion || '请参考规范' }}</div>
                    </div>
                  </td>
                  <td class="status-cell"><span class="status-tag" :class="`st-${getIssueUrgency(issue)}`">{{ getIssueUrgencyLabel(issue) }}</span></td>
                </tr>
              </template>
              <tr v-else><td colspan="5" style="text-align:center; padding: 30px; color:#9ca3af;">无样式异常数据</td></tr>
            </tbody>
          </table>

          <div
            v-if="reportData.issues && reportData.issues.length > 0 && totalFilteredCount > 0"
            class="dash-pagination-bar"
          >
            <div class="dash-pg-left">
              <span class="dash-pg-total">共 {{ totalFilteredCount }} 条</span>
              <label class="dash-pg-size">
                <span>每页</span>
                <select v-model.number="tablePageSize" class="dash-pg-select">
                  <option v-for="n in tablePageSizeOptions" :key="n" :value="n">{{ n }}</option>
                </select>
                <span>条</span>
              </label>
            </div>
            <div class="dash-pg-center">
              <button
                type="button"
                class="dash-pg-nav dash-pg-nav-icon"
                :disabled="tableCurrentPage <= 1"
                @click="tableCurrentPage = Math.max(1, tableCurrentPage - 1)"
                aria-label="上一页"
              >
                <span aria-hidden="true">‹</span>
              </button>
              <span class="dash-pg-indicator">第 {{ tableCurrentPage }} / {{ tableTotalPages }} 页</span>
              <button
                type="button"
                class="dash-pg-nav dash-pg-nav-icon"
                :disabled="tableCurrentPage >= tableTotalPages"
                @click="tableCurrentPage = Math.min(tableTotalPages, tableCurrentPage + 1)"
                aria-label="下一页"
              >
                <span aria-hidden="true">›</span>
              </button>
            </div>
          </div>

          <div class="sidebar-footer">
            <div class="fix-suggestion-box">
              <div class="fs-title"><span>🤖</span> AI 整体诊断结论</div>
              <ul v-if="diagnosisBulletHtmlList.length > 0" class="fs-bullets">
                <li v-for="(html, idx) in diagnosisBulletHtmlList" :key="idx" v-html="html"></li>
              </ul>
              <div v-else class="fs-text" v-html="dashboardDiagnosisFallbackHtml"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppNavbar from '../components/AppNavbar.vue'
import IconStroke from '../components/IconStroke.vue'
import DashboardIssuePopover from '../components/DashboardIssuePopover.vue'
import FilterSelect from '../components/FilterSelect.vue'
import { useAuditStore } from '../store/audit'
import { getIssueUrgency, getCategoryType } from '../utils/issueUrgency'
import { splitDiagnosisLines, diagnosisMarkdownBoldToHtml } from '../utils/diagnosisFormat'

const router = useRouter()
const route = useRoute()
const auditStore = useAuditStore()
const reportData = auditStore.reportData
const showGenerateReportBtn = computed(() => route.query.entry !== 'snapshot')

const textTip = ref({
  visible: false,
  text: '',
  style: {}
})

const clamp = (val, min, max) => Math.max(min, Math.min(max, val))

const updateTextTipPos = (evt) => {
  if (!textTip.value.visible) return
  const el = evt?.currentTarget
  if (!el || !el.getBoundingClientRect) return
  const rect = el.getBoundingClientRect()
  const gap = 10
  const top = rect.top + rect.height / 2
  const left = rect.right + gap
  const maxLeft = window.innerWidth - 24
  const maxTop = window.innerHeight - 24

  textTip.value.style = {
    top: `${clamp(top, 24, maxTop)}px`,
    left: `${clamp(left, 24, maxLeft)}px`,
    transform: 'translateY(-50%)'
  }
}

const onTextTipEnter = (evt, text) => {
  textTip.value.text = text || ''
  textTip.value.visible = true
  updateTextTipPos(evt)
}

const onTextTipMove = (evt) => updateTextTipPos(evt)
const onTextTipLeave = () => {
  textTip.value.visible = false
}

const diagnosisBulletHtmlList = computed(() => {
  const raw = reportData?.diagnosis
  if (!raw || typeof raw !== 'string') return []
  const lines = splitDiagnosisLines(raw)
  return lines.map((line) => diagnosisMarkdownBoldToHtml(line))
})

const dashboardDiagnosisFallbackHtml = computed(() => {
  const raw = reportData?.diagnosis
  if (!raw || typeof raw !== 'string' || !raw.trim()) return '大模型未返回整体诊断。'
  return diagnosisMarkdownBoldToHtml(raw)
})

const zoom = ref(50)
const selectedCategory = ref('all')
const tablePageSizeOptions = [10, 20, 50, 100]
const tablePageSize = ref(20)
const tableCurrentPage = ref(1)
const hoveredIssues = ref([])
const hoveredRectKey = ref(null)
const hoveredAnchorEl = ref(null)
const canvasViewportRef = ref(null)
const mockDeviceRef = ref(null)
const popoverLayerRef = ref(null)
const popoverLayerStyle = ref({})
const popoverPlacement = ref('right')

let clearHoverTimer = null
let pendingSwitchTimer = null
let popoverPosRaf = null
let hitTestRaf = null
let lastPointerEvent = null

const VIEW_PAD = 12
const EST_POP_W = 300
const HOVER_SWITCH_DELAY_MS = 300
const LEAVE_DELAY_MS = 450

function estimatePopoverHeight(n) {
  return Math.min(360, 56 + n * 108)
}

function computeCenteredInViewport(viewportRect) {
  const pad = VIEW_PAD
  const n = hoveredIssues.value.length || 1
  const popW = Math.min(EST_POP_W, viewportRect.width - pad * 2)
  const popH = Math.min(estimatePopoverHeight(n), viewportRect.height - pad * 2)
  let left = viewportRect.left + (viewportRect.width - popW) / 2
  let top = viewportRect.top + (viewportRect.height - popH) / 2
  left = Math.max(viewportRect.left + pad, Math.min(left, viewportRect.right - pad - popW))
  top = Math.max(viewportRect.top + pad, Math.min(top, viewportRect.bottom - pad - popH))
  popoverPlacement.value = 'center'
  return {
    position: 'fixed',
    left: `${Math.round(left)}px`,
    top: `${Math.round(top)}px`,
    zIndex: 2147483647,
    /* 必须可命中，否则 elementsFromPoint 会穿透到下方标注框，阅读弹窗时误切换 */
    pointerEvents: 'auto',
    maxWidth: `${Math.round(popW)}px`
  }
}

function updatePopoverPosition() {
  const viewportEl = canvasViewportRef.value
  if (!hoveredIssues.value.length || !viewportEl) return
  const v = viewportEl.getBoundingClientRect()
  popoverLayerStyle.value = computeCenteredInViewport(v)
}

function schedulePopoverPosition() {
  if (popoverPosRaf != null) cancelAnimationFrame(popoverPosRaf)
  popoverPosRaf = requestAnimationFrame(() => {
    popoverPosRaf = null
    updatePopoverPosition()
  })
}

function onWindowResizeOrScroll() {
  schedulePopoverPosition()
}

const getIssueUrgencyLabel = (issue) => {
  const u = getIssueUrgency(issue)
  if (u === 'high') return '高'
  if (u === 'medium') return '中'
  return '低'
}

function getMarkerDataId(marker, idx) {
  const id = marker.issue?.id
  if (id != null && id !== '') return String(id)
  return `m-${idx}-${marker.rect.left}-${marker.rect.top}`
}

function findIssueByDataId(rawId) {
  if (rawId == null || rawId === '') return null
  const markers = issueMarkers.value
  for (let i = 0; i < markers.length; i++) {
    if (getMarkerDataId(markers[i], i) === String(rawId)) return markers[i].issue
  }
  return null
}

function rectKey(r) {
  if (!r || typeof r !== 'object') return ''
  const q = (n) => Math.round(Number(n) || 0)
  return [q(r.left), q(r.top), q(r.width), q(r.height)].join(',')
}

function markerRectKey(marker) {
  return rectKey(marker.rect)
}

function cancelClearHover() {
  if (clearHoverTimer) clearTimeout(clearHoverTimer)
  clearHoverTimer = null
}

function clearPendingSwitch() {
  if (pendingSwitchTimer) {
    clearTimeout(pendingSwitchTimer)
    pendingSwitchTimer = null
  }
}

function scheduleClearHover(delay = LEAVE_DELAY_MS) {
  cancelClearHover()
  clearHoverTimer = setTimeout(() => {
    clearHoverTimer = null
    hoveredIssues.value = []
    hoveredRectKey.value = null
    hoveredAnchorEl.value = null
    popoverLayerStyle.value = {}
  }, delay)
}

/**
 * 在指针位置命中「面积最小」的标注框：嵌套时等价于最内层细节，不依赖 z-index 叠放（避免悬停抬升盖住内框）。
 */
function findBestAnnotationUnderPoint(clientX, clientY, device) {
  if (!device) return null
  const nodes = device.querySelectorAll('.annotation-box')
  let bestEl = null
  let bestArea = Infinity
  for (const el of nodes) {
    const r = el.getBoundingClientRect()
    if (r.width <= 0 || r.height <= 0) continue
    if (
      clientX < r.left ||
      clientX > r.right ||
      clientY < r.top ||
      clientY > r.bottom
    ) {
      continue
    }
    const area = r.width * r.height
    if (area < bestArea) {
      bestArea = area
      bestEl = el
    }
  }
  return bestEl
}

function isPointOverPopoverLayer(clientX, clientY) {
  const layer = popoverLayerRef.value
  if (!layer || !hoveredIssues.value.length) return false
  const r = layer.getBoundingClientRect()
  if (r.width <= 0 || r.height <= 0) return false
  return (
    clientX >= r.left &&
    clientX <= r.right &&
    clientY >= r.top &&
    clientY <= r.bottom
  )
}

function onDocumentPointerMove(e) {
  lastPointerEvent = e
  if (hitTestRaf != null) return
  hitTestRaf = requestAnimationFrame(() => {
    hitTestRaf = null
    const ev = lastPointerEvent
    const device = mockDeviceRef.value
    if (!ev || !device) return

    const x = ev.clientX
    const y = ev.clientY
    const stack = document.elementsFromPoint(x, y)

    const overPopover =
      stack.some((el) => el?.closest?.('.issue-popover-layer') || el?.closest?.('.dip-wrap')) ||
      isPointOverPopoverLayer(x, y)

    /* 必须先判断弹窗：几何命中标注框不区分叠放顺序，弹窗盖住预览时指针仍在下方框的 rect 内，会误切换 */
    if (overPopover) {
      cancelClearHover()
      clearPendingSwitch()
      return
    }

    const annEl = findBestAnnotationUnderPoint(x, y, device)

    if (annEl) {
      cancelClearHover()
      const issue = findIssueByDataId(annEl.dataset.issueId)
      if (!issue) return
      const rk = rectKey(issue.rect)
      if (rk === hoveredRectKey.value) {
        clearPendingSwitch()
        hoveredAnchorEl.value = annEl
        schedulePopoverPosition()
        return
      }
      const delay = hoveredRectKey.value === null ? 0 : HOVER_SWITCH_DELAY_MS
      clearPendingSwitch()
      pendingSwitchTimer = setTimeout(() => {
        pendingSwitchTimer = null
        hoveredRectKey.value = rk
        hoveredIssues.value = collectIssuesForRect(issue.rect)
        hoveredAnchorEl.value = annEl
        nextTick(() => {
          updatePopoverPosition()
          schedulePopoverPosition()
        })
      }, delay)
    } else {
      clearPendingSwitch()
      scheduleClearHover(LEAVE_DELAY_MS)
    }
  })
}

const onPopoverEnter = () => {
  cancelClearHover()
}

const onPopoverLeave = () => {
  scheduleClearHover(LEAVE_DELAY_MS)
}

const categoryOptions = [
  { value: 'all', label: '全部分类' },
  { value: 'visual', label: '视觉一致性' },
  { value: 'interaction', label: '交互体验' },
  { value: 'content', label: '文案与话术' },
  { value: 'functional', label: '功能障碍' }
]

onMounted(() => {
  if (!reportData) setTimeout(() => router.push('/'), 1500)
  window.addEventListener('resize', onWindowResizeOrScroll, { passive: true })
  window.addEventListener('scroll', onWindowResizeOrScroll, true)
  window.addEventListener('mousemove', onDocumentPointerMove, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('resize', onWindowResizeOrScroll)
  window.removeEventListener('scroll', onWindowResizeOrScroll, true)
  window.removeEventListener('mousemove', onDocumentPointerMove)
  cancelClearHover()
  clearPendingSwitch()
  if (popoverPosRaf != null) cancelAnimationFrame(popoverPosRaf)
  if (hitTestRaf != null) cancelAnimationFrame(hitTestRaf)
})

const filteredTableIssues = computed(() => {
  if (!reportData || !reportData.issues) return []
  if (selectedCategory.value === 'all') return reportData.issues
  return reportData.issues.filter(i => getCategoryType(i.category, i) === selectedCategory.value)
})

const totalFilteredCount = computed(() => filteredTableIssues.value.length)

const tableTotalPages = computed(() => {
  const n = totalFilteredCount.value
  const size = Math.max(1, Number(tablePageSize.value) || 20)
  return Math.max(1, Math.ceil(n / size))
})

const pagedTableIssues = computed(() => {
  const list = filteredTableIssues.value
  const size = Math.max(1, Number(tablePageSize.value) || 20)
  const page = Math.min(Math.max(1, tableCurrentPage.value), tableTotalPages.value)
  const start = (page - 1) * size
  return list.slice(start, start + size)
})

watch(tablePageSize, () => {
  tableCurrentPage.value = 1
})

watch(selectedCategory, () => {
  tableCurrentPage.value = 1
})

watch([totalFilteredCount, tablePageSize, tableTotalPages], () => {
  if (tableCurrentPage.value > tableTotalPages.value) {
    tableCurrentPage.value = Math.max(1, tableTotalPages.value)
  }
})

/** 同一框选矩形（rect 一致）下的全部问题，顺序与报告 issues 一致 */
function collectIssuesForRect(rect) {
  const key = rectKey(rect)
  if (!key) return []
  const matched = filteredTableIssues.value.filter((i) => i.rect && rectKey(i.rect) === key)
  const orderMap = new Map()
  if (reportData?.issues) {
    reportData.issues.forEach((issue, idx) => {
      orderMap.set(issue.id, idx)
    })
  }
  return matched.slice().sort((a, b) => {
    const oa = orderMap.get(a.id) ?? 9999
    const ob = orderMap.get(b.id) ?? 9999
    return oa - ob
  })
}

watch(zoom, () => {
  if (hoveredIssues.value.length) nextTick(() => schedulePopoverPosition())
})

/** 每条 issue 独立框选，重叠时小块在上层，便于命中相邻区域 */
const issueMarkers = computed(() => {
  const list = filteredTableIssues.value
    .filter((i) => i.rect)
    .map((issue) => ({
      issue,
      rect: issue.rect,
      urgency: getIssueUrgency(issue)
    }))
  return list.sort((a, b) => {
    const areaA = a.rect.width * a.rect.height
    const areaB = b.rect.width * b.rect.height
    return areaB - areaA
  })
})

const extractValue = (desc, isActual) => {
  if (!desc || typeof desc !== 'string') return isActual ? '异常' : '规范值'
  const match = desc.match(/\d+(\.\d+)?px|#[0-9a-fA-F]{3,6}|\d+(\.\d+)?/g)
  if (match && match.length >= 2) return isActual ? match[0] : match[1]
  if (match && match.length === 1) return isActual ? match[0] : '参考规范'
  return isActual ? '异常' : '规范值'
}

const goTo = (path) => router.push(path)
</script>

<style scoped>
.dashboard-layout { display: flex; flex-direction: column; padding-top: 60px; height: 100vh; background: #f0f2f5; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif; }
.btn { border: none; cursor: pointer; font-family: inherit; font-weight: 600; transition: background 0.2s; display: inline-flex; align-items: center; justify-content: center; box-sizing: border-box; }
.btn-primary { background: #1A6AFF; color: white; border-radius: 6px; height: 36px; padding: 0 16px; font-size: 0.85rem; }
.btn-primary:hover { background: #1557e6; }

.dashboard-main { flex: 1; display: flex; overflow: hidden; padding: 24px; gap: 24px; }

.canvas-area { flex: 1; display: flex; flex-direction: column; background: white; border-radius: 12px; border: 1px solid #e5e7eb; overflow: hidden; position: relative;}
.canvas-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; border-bottom: 1px solid #e5e7eb; background: white; z-index: 10;}
.canvas-header-title { font-weight: 700; color: #1a1d2e; font-size: 1.05rem; }
.canvas-viewport {
  flex: 1;
  background: #eef1f6;
  overflow: auto;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 40px;
  position: relative;
}

.mock-device {
  background: white;
  box-shadow: 0 20px 40px rgba(0,0,0,0.15);
  position: relative;
  transform-origin: top center;
  transition: transform 0.15s ease;
  display: inline-block;
  line-height: 0;
}

.actual-img {
  display: block;
  max-width: none;
}
.actual-img-placeholder { padding: 80px 20px; text-align: center; color: #9ca3af; height: 100%; display:flex; flex-direction:column; justify-content:center; align-items:center;}

.zoom-controls { position: absolute; bottom: 20px; right: 20px; background: white; border: 1px solid #e5e7eb; border-radius: 8px; display: flex; align-items: center; padding: 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
.zoom-controls button { background: none; border: none; padding: 4px 12px; font-size: 1.2rem; cursor: pointer; color: #4b5563; }
.zoom-controls span { font-size: 0.85rem; font-weight: 600; width: 45px; text-align: center; }

.annotation-box {
  position: absolute;
  border: 2px solid;
  box-sizing: border-box;
  cursor: pointer;
  box-shadow: 0 0 0 3px rgba(255,255,255,0.7);
  z-index: 5;
  transition: background 0.15s ease, box-shadow 0.15s ease, z-index 0.15s ease;
}
.annotation-box:hover {
  background: rgba(255,255,255,0.18);
  box-shadow:
    0 0 0 2px rgba(255,255,255,0.75),
    0 3px 12px rgba(0, 0, 0, 0.1),
    0 0 0 1px rgba(0, 0, 0, 0.04);
}
.annotation-box.is-popover-active {
  background: rgba(255,255,255,0.18);
  box-shadow:
    0 0 0 2px rgba(255,255,255,0.85),
    0 0 0 1px rgba(26, 106, 255, 0.38),
    0 4px 16px rgba(26, 106, 255, 0.14),
    0 2px 8px rgba(0, 0, 0, 0.08);
}
/* 预览区仅保留红黄蓝框线，不在框上展示优先级文字（弹窗内仍显示） */
.ann-high { border-color: #ef4444; }
.ann-medium { border-color: #f59e0b; }
.ann-low { border-color: #3b82f6; }

.issue-popover-layer {
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.12s ease, visibility 0.12s ease;
  /* 与内联 z-index 一致，保证在预览标注与侧栏之上 */
  z-index: 2147483647;
  isolation: isolate;
}
.issue-popover-layer.is-visible {
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
}

.sidebar { width: 480px; background: white; border-radius: 12px; border: 1px solid #e5e7eb; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);}
.sidebar-header { padding: 24px; border-bottom: 1px solid #e5e7eb; }
.sidebar-header-title { font-size: 1.2rem; font-weight: 700; color: #1a1d2e; margin-bottom: 8px; }
.sidebar-header-hint { font-size: 0.85rem; color: #6b7280; display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.sidebar-body { flex: 1; overflow-y: auto; display: flex; flex-direction: column; }

.audit-table { width: 100%; border-collapse: collapse; table-layout: fixed;}
.audit-table col.col-idx { width: 44px; }
.audit-table col.col-status { width: 72px; }
.th-idx { width: 44px; }
.th-status { width: 72px; text-align: left; }
.audit-table th,
.audit-table td { overflow: visible; }
.row-idx {
  color: #9ca3af;
  font-size: 12px;
  text-align: left;
}
.audit-table th {
  padding: 14px 24px;
  font-size: 12px;
  font-weight: 500;
  color: #9ca3af;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}
.group-title { padding: 20px 24px 10px; font-size: 0.95rem; font-weight: 600; color: #1a1d2e; }
.data-row { border-bottom: 1px solid #f3f4f6; }
.data-row td { padding: 16px 18px; font-size: 12px; vertical-align: top;}
.audit-table td.actual-val { padding-left: 38px; }
.audit-table td.standard-val { padding-left: 8px; }
.audit-table th { padding-left: 18px; padding-right: 18px; }
.audit-table th.th-actual { padding-left: 38px; }
.audit-table th.th-standard { padding-left: 8px; }
.row-idx { padding-left: 18px; padding-right: 18px; }
.status-cell { text-align: left; }
.th-idx { white-space: nowrap; }
.attr-name { color: #4b5563; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
.val-high { color: #ef4444; font-weight: 500; } .val-medium { color: #f59e0b; font-weight: 500; } .val-low { color: #3b82f6; font-weight: 500; }
.standard-val { color: #1a1d2e; font-weight: 500; position: relative; }
.cell-main {
  font-size: 12px;
  font-weight: 500;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.fix-link {
  color: #1A6AFF;
  font-size: 12px;
  margin-top: 0;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-word;
  cursor: pointer;
}
.tip-anchor {
  position: relative;
  display: block;
  overflow: visible;
  outline: none;
  cursor: pointer;
}
.tip-text {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.dash-text-tip {
  position: fixed;
  z-index: 2147483647;
  max-width: min(520px, 56vw);
  white-space: pre-wrap;
  word-break: break-word;
  background: #1a1d2e;
  color: #fff;
  padding: 10px 12px;
  border-radius: 10px;
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.25);
  line-height: 1.5;
  font-size: 12px;
  pointer-events: none;
}

.status-tag { padding: 3px 10px; border-radius: 6px; font-size: 12px; font-weight: 500; display: inline-block;}
.st-high { color: #ef4444; background: #fee2e2; }
.st-medium { color: #b45309; background: #fef3c7; }
.st-low { color: #2563eb; background: #dbeafe; }

.sidebar-footer { padding: 24px; margin-top: auto; border-top: 1px solid #e5e7eb;}
.fix-suggestion-box { background: #f0f4ff; border-radius: 8px; padding: 20px; }
.fs-title { font-size: 0.9rem; font-weight: 600; color: #1A6AFF; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }
.fs-title span { font-size: 16px; }
.fs-text { font-size: 0.85rem; color: #4b5563; line-height: 1.6; }
.fs-bullets {
  margin: 0;
  padding-left: 1.2em;
  font-size: 0.85rem;
  color: #4b5563;
  line-height: 1.65;
  list-style-type: disc;
}
.fs-bullets li { margin-bottom: 8px; }
.fs-bullets li:last-child { margin-bottom: 0; }
.fs-bullets li :deep(strong),
.fs-text :deep(strong) { font-weight: 700; color: #1a1d2e; }

.dash-category-select { width: 110px; min-width: 110px; flex-shrink: 0; }
.dash-category-select :deep(.filter-select-trigger) {
  height: 28px;
  padding: 0 calc(var(--input-chevron-inset, 10px) + 14px + 6px) 0 10px;
  font-size: 12px;
  border-radius: 4px;
  border-color: #e5e7eb;
  background-color: #f9fafb;
  color: #4b5563;
  background-position: right var(--input-chevron-inset, 10px) center;
  background-size: 14px;
}
.dash-category-select :deep(.filter-select-menu) {
  font-size: 12px;
  border-radius: 6px;
  min-width: 140px;
}
.dash-category-select :deep(.filter-select-option) {
  padding: 6px 10px;
  font-size: 12px;
}

.dash-pagination-bar {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 16px;
  margin: 12px 16px 0;
  background: transparent;
  border: none;
  border-radius: 0;
  font-size: 13px;
  color: #4b5563;
  flex-shrink: 0;
}
.dash-pg-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: nowrap;
}
.dash-pg-total {
  color: #6b7280;
  white-space: nowrap;
}
.dash-pg-size {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin: 0;
  cursor: pointer;
  color: #6b7280;
  white-space: nowrap;
}
.dash-pg-select {
  height: 30px;
  min-width: 52px;
  padding: 0 calc(var(--input-chevron-inset, 10px) + 14px) 0 10px;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  background-color: #fff;
  font-size: 13px;
  color: #1a1d2e;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%236b7280' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right var(--input-chevron-inset, 10px) center;
  background-size: 12px;
}
.dash-pg-select:focus {
  outline: none;
  border-color: #1a6aff;
  box-shadow: 0 0 0 2px rgba(26, 106, 255, 0.15);
}
.dash-pg-center {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: nowrap;
  justify-content: center;
  margin-left: auto;
}
.dash-pg-nav {
  height: 30px;
  padding: 0 12px;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  background: #fff;
  color: #6b7280;
  font-size: 13px;
  cursor: pointer;
  font-family: inherit;
}
.dash-pg-nav:hover:not(:disabled) {
  border-color: #d1d5db;
  color: #374151;
}
.dash-pg-nav:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.dash-pg-indicator {
  color: #6b7280;
  white-space: nowrap;
  font-size: 13px;
}
.dash-pg-nav-icon {
  width: 30px;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  line-height: 1;
}
</style>
