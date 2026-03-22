<template>
  <div v-if="reportData" class="rpt-body">
    <AppNavbar variant="report" class="no-print">
      <template #actions>
        <button class="btn btn-ghost" @click="goTo('/dashboard')">查看可视化看板</button>
        <button class="btn btn-primary" @click="exportPDF">导出报告</button>
      </template>
    </AppNavbar>

    <div class="rpt-page">
      <div class="rpt-inner">
        <div class="rpt-breadcrumb no-print">
          <a href="#" @click.prevent="goTo('/')">首页</a>
          <span class="sep">></span>
          <span>自动化走查</span>
          <span class="sep">></span>
          <span class="cur">报告详情</span>
        </div>

        <div class="rpt-page-stack">
          <div class="rpt-top-row">
            <div id="left-col" class="rpt-left-stack">
            <div class="rpt-card score-card score-tip-anchor">
              <div class="score-card-hdg">
                设计还原度评分（{{ currentModeName }}）
                <span class="score-tip-icon" @mouseenter="enterMainTip" @mouseleave="leaveMainTip">?</span>
              </div>
              <Transition name="tip-fade">
                <div v-show="showMainTip" class="score-tip-popup card-center" @mouseenter="enterMainTip" @mouseleave="leaveMainTip">
                  <div class="score-tip-title">评分计算公式</div>
                  <div class="score-tip-formula">还原度 = max(0, 100 − Σ 各维度扣分)；单维度扣分 = 权重 × 该维问题数 ÷ 检查项总数 T（T = {{ restorationDisplay.checkItemTotal }}）</div>
                  <div class="score-tip-detail">
                    <span>功能障碍 35×{{ restorationDisplay.dimensionCounts.functional }}÷T = {{ formatDed(restorationDisplay.dimensionDeductions.functional) }}</span>
                    <span>交互体验 30×{{ restorationDisplay.dimensionCounts.interaction }}÷T = {{ formatDed(restorationDisplay.dimensionDeductions.interaction) }}</span>
                    <span>视觉一致性 20×{{ restorationDisplay.dimensionCounts.visual }}÷T = {{ formatDed(restorationDisplay.dimensionDeductions.visual) }}</span>
                    <span>文案与话术 15×{{ restorationDisplay.dimensionCounts.content }}÷T = {{ formatDed(restorationDisplay.dimensionDeductions.content) }}</span>
                    <span>合计扣分 {{ formatDed(restorationTotalDeduction) }} → 总还原度 {{ displayScore }} 分</span>
                  </div>
                </div>
              </Transition>
              <Transition name="tip-fade">
                <div v-if="activeDimTip" class="score-tip-popup card-center" @mouseenter="enterDimTip(activeDimTip)" @mouseleave="leaveDimTip">
                  <div class="score-tip-title">{{ dimTipLabel }} — 维度说明</div>
                  <div class="score-tip-formula">该维度单项分 = max(0, 100 − 权重×问题数÷T)；本维度权重 {{ activeDimWeight }}</div>
                  <div class="score-tip-detail">
                    <span>本维问题数 {{ activeDimCount }}，T = {{ restorationDisplay.checkItemTotal }}</span>
                    <span>本维扣分 = {{ activeDimWeight }} × {{ activeDimCount }} ÷ {{ restorationDisplay.checkItemTotal }} = {{ formatDed(activeDimDeduction) }}</span>
                    <span>本维单项分 {{ dimensionScores[activeDimTip] }} 分</span>
                  </div>
                </div>
              </Transition>
              <div class="score-body">
                <div class="ring-wrap">
                  <svg class="ring-svg" width="110" height="110" viewBox="0 0 110 110">
                    <circle class="ring-bg" cx="55" cy="55" r="44" />
                    <circle class="ring-fg" cx="55" cy="55" r="44"
                      :stroke-dashoffset="276.5 - (276.5 * (displayScore || 0) / 100)"
                      stroke-dasharray="276.5" />
                  </svg>
                  <div class="ring-label">
                    <span class="ring-pct">{{ displayScore || 0 }}%</span>
                    <span class="ring-sub">总评分</span>
                  </div>
                </div>
                <div class="score-detail">
                  <div class="score-badge" :class="scoreBadgeClass">{{ scoreBadgeText }}</div>
                  <div class="score-desc">本次走查发现 {{ reportData.issueCount || 0 }} 个规范问题。建议优先修复高优问题。</div>
                  <div class="score-stats">
                    <div class="stat-block">
                      <div class="stat-val">{{ dimensionScores.functional }}<span class="stat-unit">分</span></div>
                      <div class="stat-label">功能障碍 <span class="score-tip-icon sm" @mouseenter="enterDimTip('functional')" @mouseleave="leaveDimTip">?</span></div>
                    </div>
                    <div class="stat-block">
                      <div class="stat-val">{{ dimensionScores.interaction }}<span class="stat-unit">分</span></div>
                      <div class="stat-label">交互体验 <span class="score-tip-icon sm" @mouseenter="enterDimTip('interaction')" @mouseleave="leaveDimTip">?</span></div>
                    </div>
                    <div class="stat-block">
                      <div class="stat-val">{{ dimensionScores.visual }}<span class="stat-unit">分</span></div>
                      <div class="stat-label">视觉一致性 <span class="score-tip-icon sm" @mouseenter="enterDimTip('visual')" @mouseleave="leaveDimTip">?</span></div>
                    </div>
                    <div class="stat-block">
                      <div class="stat-val">{{ dimensionScores.content }}<span class="stat-unit">分</span></div>
                      <div class="stat-label">文案与话术 <span class="score-tip-icon sm" @mouseenter="enterDimTip('content')" @mouseleave="leaveDimTip">?</span></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="rpt-card distribution-card">
              <div class="distribution-hd">关键问题分布</div>
              <div class="distribution-body">
                <div class="distribution-chart">
                  <div class="chart-item" v-for="(item, idx) in topIssueCategories" :key="idx">
                    <div class="chart-info">
                      <span class="chart-label">{{ item.name }}</span>
                      <span class="chart-count">{{ item.count }} 个问题 ({{ item.percentage }}%)</span>
                    </div>
                    <div class="chart-bar-wrap">
                      <div class="chart-bar" :style="{ width: item.percentage + '%', background: item.color }"></div>
                    </div>
                  </div>
                </div>
                <div class="distribution-summary">
                  <div class="summary-label">AI 问题总结</div>
                  <ul v-if="diagnosisBullets.length > 0" class="summary-bullets">
                    <li v-for="(line, idx) in diagnosisBullets" :key="idx">{{ line }}</li>
                  </ul>
                  <div v-else class="summary-text">{{ reportData.diagnosis || '暂无 AI 总结' }}</div>
                </div>
              </div>
            </div>
            </div>

            <div class="rpt-sidebar">
            <div class="meta-card">
              <div class="meta-card-hd">报告元数据</div>
              <div class="meta-row">
                <span class="meta-lbl">目标页面</span>
                <span class="meta-val"><a :href="formattedUrl" target="_blank">点击访问</a></span>
              </div>
              <div class="meta-row">
                <span class="meta-lbl">操作员</span>
                <span class="meta-val">{{ userStore.userInfo ? userStore.userInfo.username : 'Agent' }}</span>
              </div>
              <div class="meta-row">
                <span class="meta-lbl">走查模式</span>
                <span class="meta-val">{{ currentModeName }}</span>
              </div>
            </div>

            <div class="meta-card snapshot-card">
              <div class="snapshot-title">实际页面快照</div>
              <img
                v-if="reportData.screenshot"
                :src="screenshotSrc"
                class="snapshot-img"
                @click="goTo('/dashboard')"
              />
              <div v-else class="snapshot-placeholder">此条走查记录暂无快照数据</div>
            </div>

            <div class="help-card no-print">
              <div class="help-title">需要帮助？</div>
              <div class="help-desc">如需更多帮助请点击此处</div>
              <div class="help-btn-wrap">
                <button type="button" class="help-btn">反馈问题</button>
                <div class="help-tooltip">此功能开发中，敬请期待</div>
              </div>
            </div>

            <div class="trend-card no-print">
              <div class="trend-title">近期历史还原度趋势</div>
              <div class="trend-chart" v-if="trendData.length > 0">
                <div class="bar-wrap" v-for="(item, idx) in trendData" :key="idx">
                  <div class="bar-val" :style="{ color: idx === trendData.length - 1 ? '#1A6AFF' : '#9ca3af' }">{{ item.score }}%</div>
                  <div class="bar-fill" :class="{ today: idx === trendData.length - 1 }" :style="'height:' + Math.max(item.score * 0.6, 10) + 'px'"></div>
                  <div class="bar-date">{{ item.date }}</div>
                </div>
              </div>
              <div v-else class="trend-empty">暂无足够历史数据</div>
            </div>
          </div>
        </div>

        <div class="rpt-issues-section">
          <div class="issue-list-hd">
            <div class="issue-list-title">关键问题清单 <span class="issue-list-cnt">{{ filteredIssues.length }}</span></div>
          </div>
          <div class="issue-tabs-row no-print">
            <div class="issue-tabs-main">
              <button class="tab-btn" :class="{ active: activeTab === 'all' }" @click="activeTab = 'all'">
                全部问题 <span class="tab-badge">{{ allIssues.length }}</span>
              </button>
              <button class="tab-btn" :class="{ active: activeTab === 'functional' }" @click="activeTab = 'functional'">
                功能障碍 <span class="tab-badge">{{ functionalIssues.length }}</span>
              </button>
              <button class="tab-btn" :class="{ active: activeTab === 'interaction' }" @click="activeTab = 'interaction'">
                交互体验 <span class="tab-badge">{{ interactionIssues.length }}</span>
              </button>
              <button class="tab-btn" :class="{ active: activeTab === 'visual' }" @click="activeTab = 'visual'">
                视觉一致性 <span class="tab-badge">{{ visualIssues.length }}</span>
              </button>
              <button
                type="button"
                class="tab-btn"
                :class="{ active: activeTab === 'content' }"
                title="检测全局文案风格是否一致，以及同类功能下提示、弹窗等用语是否统一"
                @click="activeTab = 'content'"
              >
                文案与话术 <span class="tab-badge">{{ contentIssues.length }}</span>
              </button>
              <span class="tab-divider" aria-hidden="true"></span>
              <div class="urgency-group">
                <button type="button" class="urgency-btn urgency-high" :class="{ 'is-active': activeUrgency === 'high' }" @click="toggleUrgency('high')">
                  高
                </button>
                <button type="button" class="urgency-btn urgency-medium" :class="{ 'is-active': activeUrgency === 'medium' }" @click="toggleUrgency('medium')">
                  中
                </button>
                <button type="button" class="urgency-btn urgency-low" :class="{ 'is-active': activeUrgency === 'low' }" @click="toggleUrgency('low')">
                  低
                </button>
              </div>
            </div>
            <div v-if="ignoredIssues.length > 0" class="ignored-bar">
              <span class="ignored-hint">已忽略 {{ ignoredIssues.length }} 项</span>
              <button type="button" class="ignored-toggle" @click="showIgnored = !showIgnored">{{ showIgnored ? '隐藏已忽略' : '查看已忽略' }}</button>
              <button type="button" class="ignored-restore-all" @click="restoreAllIgnored">全部恢复</button>
            </div>
          </div>

          <div class="issue-card" :class="{ 'issue-card--ignored': ignoredIds.has(issue.id) }" v-for="issue in pagedIssues" :key="issue.id">
            <div class="issue-card-row">
              <div class="issue-thumb" @click="openPreview(issue)">
                <span class="thumb-mode-badge">{{ currentModeName }}</span>
                <div
                  v-if="reportData.screenshot && issue.rect"
                  class="real-thumb-crop"
                  :style="getThumbStyle(issue.rect)"
                >
                  <div class="real-thumb-box" :style="getThumbBoxStyle(issue.rect)"></div>
                </div>
                <div v-else class="issue-thumb-inner">
                  <div class="tb tb-light"></div>
                  <div class="tb tb-red"></div>
                  <div class="tb tb-light"></div>
                </div>
                <div class="issue-thumb-footer no-print">点击放大查看</div>
              </div>
              <div class="issue-body">
                <div class="issue-badge-row">
                  <span class="issue-badge" :class="getUrgencyMeta(issue).badgeClass">
                    {{ getUrgencyMeta(issue).label }}
                  </span>
                  <span class="issue-tag" :style="{ background: getIssueTag(issue).bg, color: getIssueTag(issue).color }">{{ getIssueTag(issue).label }}</span>
                  <span class="issue-assignee">{{ getCategoryLabel(issue) }}</span>
                  <button type="button" class="ignore-btn no-print" @click="toggleIgnore(issue.id)">
                    {{ ignoredIds.has(issue.id) ? '恢复' : '忽略' }}
                  </button>
                </div>
                <div class="issue-title">{{ issue.title }}</div>
                <div class="issue-desc">{{ issue.desc }}</div>
                <div class="issue-fix">
                  <div class="issue-fix-label">修复建议：</div>
                  <div class="issue-fix-text">{{ issue.suggestion }}</div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="filteredIssues.length === 0" class="empty-state">
            当前分类下暂无问题。
          </div>

          <div v-if="filteredIssues.length > 0" class="issue-pagination no-print">
            <div class="pagination-row">
              <span class="pagination-total">共 {{ filteredIssues.length }} 条</span>
              <label class="pagination-size">
                每页
                <select v-model.number="issuePageSize" class="pagination-select">
                  <option v-for="n in issuePageSizeOptions" :key="n" :value="n">{{ n }}</option>
                </select>
                条
              </label>
              <div class="pagination-nav">
                <button type="button" class="pagination-btn" :disabled="issuePage <= 1" @click="issuePage--">上一页</button>
                <span class="pagination-pages">第 {{ issuePage }} / {{ issueTotalPages }} 页</span>
                <button type="button" class="pagination-btn" :disabled="issuePage >= issueTotalPages" @click="issuePage++">下一页</button>
              </div>
              <div class="pagination-jump">
                <span class="pagination-jump-lbl">跳转</span>
                <input
                  v-model="jumpPageInput"
                  type="text"
                  inputmode="numeric"
                  class="pagination-input"
                  :placeholder="'1-' + issueTotalPages"
                  @keyup.enter="jumpToIssuePage"
                />
                <button type="button" class="pagination-btn pagination-btn-go" @click="jumpToIssuePage">确定</button>
              </div>
            </div>
          </div>

          <div v-if="showIgnored && ignoredIssues.length > 0" class="ignored-section no-print">
            <div class="ignored-section-title">已忽略的问题（{{ ignoredIssues.length }}）</div>
            <div class="issue-card issue-card--ignored" v-for="issue in ignoredIssues" :key="'ign-' + issue.id">
              <div class="issue-card-row">
                <div class="issue-body">
                  <div class="issue-badge-row">
                    <span class="issue-badge" :class="getUrgencyMeta(issue).badgeClass">{{ getUrgencyMeta(issue).label }}</span>
                    <span class="issue-tag" :style="{ background: getIssueTag(issue).bg, color: getIssueTag(issue).color }">{{ getIssueTag(issue).label }}</span>
                    <span class="issue-assignee">{{ getCategoryLabel(issue) }}</span>
                    <button type="button" class="ignore-btn ignore-btn--restore" @click="toggleIgnore(issue.id)">恢复</button>
                  </div>
                  <div class="issue-title">{{ issue.title }}</div>
                  <div class="issue-desc">{{ issue.desc }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  </div>
  <div v-else class="loading-state">加载中...</div>

  <div v-if="previewIssue" class="preview-overlay" @click.self="previewIssue = null">
    <div class="preview-modal">
      <div class="preview-header">
        <span class="preview-mode-badge">{{ currentModeName }}</span>
        <span class="preview-title">{{ previewIssue.title }}</span>
        <button class="preview-close" @click="previewIssue = null">X</button>
      </div>
      <div class="preview-body">
        <div
          v-if="reportData.screenshot && previewIssue.rect"
          class="preview-crop"
          :style="getPreviewStyle(previewIssue.rect)"
        >
          <div class="preview-box" :style="getPreviewBoxStyle(previewIssue.rect)"></div>
        </div>
        <div v-else class="preview-empty">暂无截图数据</div>
      </div>
      <div class="preview-footer">
        <span class="issue-tag" :style="{ background: getIssueTag(previewIssue).bg, color: getIssueTag(previewIssue).color }">{{ getIssueTag(previewIssue).label }}</span>
        <span class="preview-desc">{{ previewIssue.desc }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import AppNavbar from '../components/AppNavbar.vue'
import { useAuditStore } from '../store/audit'
import { useUserStore } from '../store/user'
import axios from 'axios'
import { getCategoryType, getIssueUrgency as getUrgency } from '../utils/issueUrgency'
import { computeRestorationScore, RESTORATION_WEIGHTS } from '../utils/restorationScore'

const router = useRouter()
const auditStore = useAuditStore()
const userStore = useUserStore()
const reportData = auditStore.reportData

/** AI 总结：优先按换行分段，否则按句号/叹号/问号拆成多条，便于分点阅读 */
const diagnosisBullets = computed(() => {
  const raw = reportData?.diagnosis
  if (!raw || typeof raw !== 'string') return []
  const t = raw.trim()
  if (!t) return []
  let parts = t.split(/\n+/).map((s) => s.trim()).filter(Boolean)
  if (parts.length === 1) {
    parts = parts[0].split(/[。！？]+/).map((s) => s.trim()).filter(Boolean)
  }
  return parts
})

const activeTab = ref('all')
/** null 表示不按紧急度筛选（显示当前分类下全部） */
const activeUrgency = ref(null)

const ignoredIds = ref(new Set())
const showIgnored = ref(false)
const toggleIgnore = (id) => {
  const s = new Set(ignoredIds.value)
  if (s.has(id)) s.delete(id); else s.add(id)
  ignoredIds.value = s
}
const restoreAllIgnored = () => { ignoredIds.value = new Set() }

const toggleUrgency = (level) => {
  activeUrgency.value = activeUrgency.value === level ? null : level
}
const trendData = ref([])
const previewIssue = ref(null)
const showMainTip = ref(false)
let mainTipTimer = null
const enterMainTip = () => { clearTimeout(mainTipTimer); showMainTip.value = true }
const leaveMainTip = () => { mainTipTimer = setTimeout(() => { showMainTip.value = false }, 120) }

const activeDimTip = ref(null)
let dimTipTimer = null
const enterDimTip = (key) => { clearTimeout(dimTipTimer); activeDimTip.value = key }
const leaveDimTip = () => { dimTipTimer = setTimeout(() => { activeDimTip.value = null }, 120) }

const dimTipLabels = { functional: '功能障碍', interaction: '交互体验', visual: '视觉一致性', content: '文案与话术' }
const dimTipLabel = computed(() => dimTipLabels[activeDimTip.value] || '')

function formatDed(v) {
  if (v == null || Number.isNaN(Number(v))) return '0.00'
  return Number(v).toFixed(2)
}

const getCategoryLabel = (issue) => {
  const labels = { visual: '视觉一致性', interaction: '交互体验', content: '文案与话术', functional: '功能障碍' }
  return labels[getCategoryType(issue?.category, issue)] || issue?.category
}

const urgencyMetaMap = {
  high: { label: '高', badgeClass: 'badge-high' },
  medium: { label: '中', badgeClass: 'badge-medium' },
  low: { label: '低', badgeClass: 'badge-low' }
}

const getUrgencyMeta = (issue) => urgencyMetaMap[getUrgency(issue)] || urgencyMetaMap.low

const issueTagMap = [
  { keywords: ['字体', '字号', '字阶', 'font'], label: '字体', bg: '#eef2ff', color: '#4338ca' },
  { keywords: ['颜色', '色盘', '色值', '品牌色', 'color'], label: '颜色', bg: '#fef2f2', color: '#dc2626' },
  { keywords: ['间距', 'margin', 'padding', 'spacing'], label: '间距', bg: '#f0fdf4', color: '#16a34a' },
  { keywords: ['圆角', 'radius'], label: '圆角', bg: '#fffbeb', color: '#d97706' },
  { keywords: ['行高', 'line-height'], label: '行高', bg: '#faf5ff', color: '#9333ea' },
  { keywords: ['字重', 'font-weight'], label: '字重', bg: '#eef2ff', color: '#4338ca' },
  { keywords: ['按钮', 'button', 'btn'], label: '按钮', bg: '#eff6ff', color: '#2563eb' },
  { keywords: ['输入框', 'input', '表单', '选择器'], label: '表单', bg: '#f0fdf4', color: '#16a34a' },
  { keywords: ['导航', 'nav', '分页'], label: '导航', bg: '#fefce8', color: '#ca8a04' },
  { keywords: ['点击', '热区', '光标', 'cursor'], label: '交互', bg: '#fff7ed', color: '#ea580c' },
  { keywords: ['对比度', '无障碍', 'alt', '标题层级'], label: '无障碍', bg: '#fdf2f8', color: '#db2777' },
  { keywords: ['投影', '阴影', 'shadow'], label: '阴影', bg: '#f5f3ff', color: '#7c3aed' },
  { keywords: ['动画', '过渡', 'transition'], label: '动效', bg: '#ecfeff', color: '#0891b2' },
  { keywords: ['栅格', 'grid', '容器'], label: '栅格', bg: '#f0f9ff', color: '#0284c7' },
  { keywords: ['图片', 'img', '体积'], label: '图片', bg: '#fefce8', color: '#ca8a04' },
  { keywords: ['中英文', '空格', '日期', '死链', '文案'], label: '文案', bg: '#f0fdf4', color: '#16a34a' },
  { keywords: ['布局', '溢出', '省略', 'z-index', '层级'], label: '布局', bg: '#fff1f2', color: '#e11d48' },
  { keywords: ['表格', 'table', '行高'], label: '表格', bg: '#f8fafc', color: '#475569' },
  { keywords: ['标签', 'tag'], label: '标签', bg: '#faf5ff', color: '#9333ea' }
]

const getIssueTag = (issue) => {
  const t = issue?.title || ''
  if (t.includes('图片体积过大')) {
    return { label: '资源', bg: '#fff7ed', color: '#c2410c' }
  }
  const text = (t + (issue.category || '')).toLowerCase()
  for (const rule of issueTagMap) {
    if (rule.keywords.some(kw => text.includes(kw))) {
      return rule
    }
  }
  return { label: '样式', bg: '#f3f4f6', color: '#6b7280' }
}

const currentModeName = computed(() => {
  const m = auditStore.checkMode
  if (m === 'baseline' || m === 'static_scan') return '基准值模式'
  if (m === 'design') return '设计稿模式'
  if (m === 'component') return '组件模式'
  return '基准值模式'
})

const rawIssues = computed(() => reportData && reportData.issues ? reportData.issues : [])
const allIssues = computed(() => rawIssues.value.filter(i => !ignoredIds.value.has(i.id)))
const ignoredIssues = computed(() => rawIssues.value.filter(i => ignoredIds.value.has(i.id)))

const visualIssues = computed(() => allIssues.value.filter(i => getCategoryType(i.category, i) === 'visual'))
const interactionIssues = computed(() => allIssues.value.filter(i => getCategoryType(i.category, i) === 'interaction'))
const contentIssues = computed(() => allIssues.value.filter(i => getCategoryType(i.category, i) === 'content'))
const functionalIssues = computed(() => allIssues.value.filter(i => getCategoryType(i.category, i) === 'functional'))

const categoryFilteredIssues = computed(() => {
  if (activeTab.value === 'visual') return visualIssues.value
  if (activeTab.value === 'interaction') return interactionIssues.value
  if (activeTab.value === 'content') return contentIssues.value
  if (activeTab.value === 'functional') return functionalIssues.value
  return allIssues.value
})

const urgencyCounts = computed(() => ({
  high: categoryFilteredIssues.value.filter(i => getUrgency(i) === 'high').length,
  medium: categoryFilteredIssues.value.filter(i => getUrgency(i) === 'medium').length,
  low: categoryFilteredIssues.value.filter(i => getUrgency(i) === 'low').length
}))

const issuePageSizeOptions = [10, 20, 50, 100]
const issuePageSize = ref(20)
const issuePage = ref(1)
const jumpPageInput = ref('')

watch(activeTab, () => {
  issuePage.value = 1
  if (activeUrgency.value !== null && urgencyCounts.value[activeUrgency.value] === 0) {
    activeUrgency.value = null
  }
})

watch(activeUrgency, () => {
  issuePage.value = 1
})

const filteredIssues = computed(() => {
  if (activeUrgency.value === null) return categoryFilteredIssues.value
  return categoryFilteredIssues.value.filter(i => getUrgency(i) === activeUrgency.value)
})

const issueTotalPages = computed(() => {
  const total = filteredIssues.value.length
  if (total === 0) return 1
  return Math.ceil(total / issuePageSize.value)
})

const pagedIssues = computed(() => {
  const list = filteredIssues.value
  const size = issuePageSize.value
  const maxPage = Math.max(1, Math.ceil(list.length / size) || 1)
  const page = Math.min(Math.max(1, issuePage.value), maxPage)
  const start = (page - 1) * size
  return list.slice(start, start + size)
})

watch(issuePageSize, () => {
  issuePage.value = 1
})

watch([filteredIssues, issuePageSize], () => {
  const total = filteredIssues.value.length
  const maxPage = Math.max(1, Math.ceil(total / issuePageSize.value) || 1)
  if (issuePage.value > maxPage) issuePage.value = maxPage
}, { deep: true })

const jumpToIssuePage = () => {
  const raw = String(jumpPageInput.value).trim()
  if (!raw) return
  const p = parseInt(raw, 10)
  if (Number.isNaN(p) || p < 1) return
  issuePage.value = Math.min(p, issueTotalPages.value)
  jumpPageInput.value = ''
}

const countByLevel = (issues) => {
  const h = issues.filter(i => i.level === 'high').length
  const m = issues.filter(i => i.level === 'medium').length
  const l = issues.filter(i => i.level === 'low' || i.level === 'warning').length
  return { h, m, l }
}

const restorationDisplay = computed(() =>
  computeRestorationScore(allIssues.value, reportData?.checkItemTotal)
)
const displayScore = computed(() => restorationDisplay.value.score)
const dimensionScores = computed(() => restorationDisplay.value.dimensionScores)
const restorationTotalDeduction = computed(() => {
  const d = restorationDisplay.value.dimensionDeductions
  return (d.functional || 0) + (d.interaction || 0) + (d.visual || 0) + (d.content || 0)
})

const scoreBadgeClass = computed(() => {
  const s = displayScore.value
  if (s >= 90) return 'badge-good'
  if (s >= 70) return 'badge-ok'
  return 'badge-bad'
})

const scoreBadgeText = computed(() => {
  const s = displayScore.value
  if (s >= 90) return '表现优秀，基本符合规范'
  if (s >= 70) return '存在部分偏差，建议修复'
  return '偏离度较高，需重点整改'
})

const activeDimWeight = computed(() =>
  activeDimTip.value ? RESTORATION_WEIGHTS[activeDimTip.value] : 0
)
const activeDimCount = computed(() =>
  activeDimTip.value ? restorationDisplay.value.dimensionCounts[activeDimTip.value] : 0
)
const activeDimDeduction = computed(() =>
  activeDimTip.value ? restorationDisplay.value.dimensionDeductions[activeDimTip.value] : 0
)

const scoreBreakdown = computed(() => ({
  all: countByLevel(allIssues.value),
  visual: countByLevel(visualIssues.value),
  interaction: countByLevel(interactionIssues.value),
  content: countByLevel(contentIssues.value),
  functional: countByLevel(functionalIssues.value)
}))

const topIssueCategories = computed(() => {
  const counts = {}
  allIssues.value.forEach(i => {
    const t = getCategoryType(i.category, i)
    counts[t] = (counts[t] || 0) + 1
  })
  const total = allIssues.value.length || 1
  const cats = [
    { name: '视觉一致性', key: 'visual', color: '#1A6AFF' },
    { name: '交互体验', key: 'interaction', color: '#f59e0b' },
    { name: '文案与话术', key: 'content', color: '#10b981' },
    { name: '功能障碍', key: 'functional', color: '#ef4444' }
  ]
  return cats
    .map(c => ({
      name: c.name,
      count: counts[c.key] || 0,
      percentage: Math.round(((counts[c.key] || 0) / total) * 100),
      color: c.color
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 4)
})

const formattedUrl = computed(() => {
  if (!reportData || !reportData.url) return '#'
  let url = reportData.url
  if (!/^https?:\/\//i.test(url)) url = 'http://' + url
  return url
})

const screenshotSrc = computed(() => {
  if (!reportData || !reportData.screenshot) return ''
  return 'data:image/png;base64,' + reportData.screenshot
})

onMounted(async () => {
  if (!reportData) {
    router.push('/')
    return
  }
  if (reportData.mode) {
    auditStore.setCheckMode(reportData.mode)
  }
  if (userStore.userInfo) {
    try {
      const res = await axios.get('http://localhost:8000/api/history/' + userStore.userInfo.id)
      if (res.data.status === 'success') {
        const history = res.data.data
        if (history && history.length > 0) {
          const recent4 = history.slice(0, 4).reverse()
          trendData.value = recent4.map(h => ({
            score: h.score || 0,
            date: h.created_at ? h.created_at.substring(5, 10) : '?'
          }))
        }
      }
    } catch (e) {
      console.error('trend data error', e)
    }
  }
})

const exportPDF = () => window.print()
const goTo = (path) => router.push(path)
const openPreview = (issue) => { previewIssue.value = issue }

const THUMB_PAD = 80
const getThumbStyle = (rect) => {
  const x = Math.max(0, rect.left - THUMB_PAD)
  const y = Math.max(0, rect.top - THUMB_PAD)
  return {
    backgroundImage: 'url(' + screenshotSrc.value + ')',
    backgroundPosition: '-' + x + 'px -' + y + 'px'
  }
}
const getThumbBoxStyle = (rect) => {
  const xOff = rect.left < THUMB_PAD ? rect.left : THUMB_PAD
  const yOff = rect.top < THUMB_PAD ? rect.top : THUMB_PAD
  return {
    top: yOff + 'px',
    left: xOff + 'px',
    width: rect.width + 'px',
    height: rect.height + 'px'
  }
}

const PREVIEW_PAD = 150
const getPreviewStyle = (rect) => {
  const x = Math.max(0, rect.left - PREVIEW_PAD)
  const y = Math.max(0, rect.top - PREVIEW_PAD)
  return {
    backgroundImage: 'url(' + screenshotSrc.value + ')',
    backgroundPosition: '-' + x + 'px -' + y + 'px',
    width: (rect.width + PREVIEW_PAD * 2) + 'px',
    height: (rect.height + PREVIEW_PAD * 2) + 'px'
  }
}
const getPreviewBoxStyle = (rect) => {
  const xOff = rect.left < PREVIEW_PAD ? rect.left : PREVIEW_PAD
  const yOff = rect.top < PREVIEW_PAD ? rect.top : PREVIEW_PAD
  return {
    top: yOff + 'px',
    left: xOff + 'px',
    width: rect.width + 'px',
    height: rect.height + 'px'
  }
}
</script>

<style scoped>
.rpt-body { background: #f4f6fb; min-height: 100vh; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif; }
.rpt-page { padding-top: 80px; padding-bottom: 60px; }
.rpt-inner { max-width: 1080px; margin: 0 auto; padding: 0 24px; }
.rpt-breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.85rem; color: #9ca3af; margin-bottom: 22px; }
.rpt-breadcrumb a { color: #6b7280; text-decoration: none; }
.rpt-breadcrumb a:hover { color: #1A6AFF; }
.rpt-breadcrumb .cur { color: #1a1d2e; font-weight: 500; }
.rpt-page-stack { width: 100%; }
.rpt-top-row {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 20px;
  align-items: stretch;
}
.rpt-left-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
  height: 100%;
}
.rpt-left-stack > .rpt-card { margin-bottom: 0; }
.rpt-issues-section {
  width: 100%;
  margin-top: 20px;
  min-width: 0;
}
.btn { border: none; font-family: inherit; cursor: pointer; transition: all 0.2s; font-weight: 600; }
.btn-primary { background: #1A6AFF; color: white; border-radius: 6px; height: 36px; padding: 0 16px; font-size: 0.85rem; display: inline-flex; align-items: center; box-sizing: border-box; }
.btn-primary:hover { background: #1557e6; }
.btn-ghost { background: transparent; color: #6b7280; border: 1px solid #e8eaf0; border-radius: 6px; height: 36px; padding: 0 16px; font-size: 0.85rem; display: inline-flex; align-items: center; box-sizing: border-box; }
.btn-ghost:hover { background: #f9fafb; color: #1a1d2e; }
.rpt-card { background: #fff; border: 1px solid #e8eaf0; border-radius: 14px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(60,72,120,.04); overflow: hidden; }
.score-card { padding: 22px 24px; }
.score-card-hdg { font-size: 1rem; font-weight: 700; color: #1a1d2e; margin-bottom: 20px; }

.score-tip-anchor { position: relative; }
.score-tip-wrap { position: relative; }
.score-tip-icon {
  display: inline-flex; align-items: center; justify-content: center;
  width: 18px; height: 18px; border-radius: 50%;
  background: #e8eaf0; color: #6b7280; font-size: 11px; font-weight: 700;
  cursor: help; margin-left: 6px; vertical-align: middle;
  transition: background 0.15s, color 0.15s;
}
.score-tip-icon.sm { width: 14px; height: 14px; font-size: 9px; margin-left: 4px; }
.score-tip-icon:hover { background: #1A6AFF; color: #fff; }
.score-tip-popup {
  display: none; position: absolute; z-index: 100;
  background: #1a1d2e; color: #fff; border-radius: 10px;
  padding: 14px 18px; min-width: 280px; max-width: 360px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.22);
  font-size: 0.78rem; line-height: 1.6;
  pointer-events: none;
}
.score-tip-popup.card-center {
  display: block; pointer-events: auto;
  top: 50%; left: 50%; transform: translate(-50%, -50%);
  min-width: 320px;
}
.score-tip-popup.card-center::after { display: none; }
.tip-fade-enter-active, .tip-fade-leave-active { transition: opacity 0.2s ease; }
.tip-fade-enter-from, .tip-fade-leave-to { opacity: 0; }
.score-tip-title { font-weight: 700; margin-bottom: 6px; font-size: 0.82rem; color: #dbeafe; }
.score-tip-formula { font-family: 'SF Mono', 'Menlo', monospace; font-size: 0.76rem; background: rgba(255,255,255,0.08); padding: 6px 10px; border-radius: 6px; margin-bottom: 8px; color: #93c5fd; word-break: break-all; }
.score-tip-detail { display: flex; flex-direction: column; gap: 2px; color: #d1d5db; font-size: 0.74rem; }
.score-body { display: flex; align-items: flex-start; gap: 28px; }
.ring-wrap { position: relative; width: 110px; height: 110px; flex-shrink: 0; }
.ring-svg { transform: rotate(-90deg); }
.ring-bg { fill: none; stroke: #eef2ff; stroke-width: 10; }
.ring-fg { fill: none; stroke: #1A6AFF; stroke-width: 10; stroke-linecap: round; transition: stroke-dashoffset 1s ease; }
.ring-label { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.ring-pct { font-size: 1.6rem; font-weight: 800; color: #1A6AFF; line-height: 1; }
.ring-sub { font-size: 0.68rem; color: #9ca3af; margin-top: 3px; }
.score-detail { flex: 1; }
.score-badge { display: inline-flex; padding: 4px 12px; border-radius: 99px; font-size: 0.78rem; font-weight: 600; margin-bottom: 12px; }
.badge-good { background: #d1fae5; color: #065f46; }
.badge-ok { background: #fef3c7; color: #92400e; }
.badge-bad { background: #fee2e2; color: #991b1b; }
.score-desc { font-size: 0.86rem; color: #6b7280; line-height: 1.75; margin-bottom: 18px; }
.score-stats { display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; }
.stat-block { flex: 1; min-width: 80px; }
.stat-val { font-size: 1.2rem; font-weight: 800; color: #1a1d2e; display: inline-flex; align-items: baseline; gap: 2px; }
.stat-unit { font-size: 0.72em; font-weight: 700; color: #6b7280; }
.stat-label { font-size: 0.75rem; color: #9ca3af; margin-top: 4px; }
.distribution-card {
  padding: 22px 24px;
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.distribution-hd { font-size: 1rem; font-weight: 700; color: #1a1d2e; margin-bottom: 18px; flex-shrink: 0; }
.distribution-body { display: flex; flex-direction: column; gap: 20px; flex: 1; min-height: 0; }
.distribution-chart { display: flex; flex-direction: column; gap: 24px; }
.chart-item { display: flex; flex-direction: column; gap: 8px; }
.chart-bar-wrap { width: 100%; height: 8px; background: #f3f4f6; border-radius: 4px; overflow: hidden; }
.chart-bar { height: 100%; border-radius: 4px; transition: width 0.5s ease; }
.chart-info { display: flex; justify-content: space-between; align-items: center; }
.chart-label { font-size: 0.85rem; font-weight: 600; color: #1a1d2e; }
.chart-count { font-size: 0.8rem; color: #6b7280; }
.distribution-summary {
  background: #f8faff;
  border-left: 3px solid #1A6AFF;
  padding: 14px 16px;
  border-radius: 0 8px 8px 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 120px;
}
.summary-label { font-size: 0.75rem; color: #1A6AFF; font-weight: 700; margin-bottom: 8px; flex-shrink: 0; }
.summary-text { font-size: 0.85rem; color: #4b5563; line-height: 1.6; flex: 1; min-height: 4em; overflow-y: auto; }
.summary-bullets {
  margin: 0;
  padding-left: 1.2em;
  font-size: 0.85rem;
  color: #4b5563;
  line-height: 1.65;
  flex: 1;
  min-height: 4em;
  overflow-y: auto;
  list-style-type: disc;
}
.summary-bullets li { margin-bottom: 10px; padding-left: 2px; }
.summary-bullets li:last-child { margin-bottom: 0; }
.issue-list-hd { margin-bottom: 12px; }
.issue-list-title { font-weight: 700; font-size: 1rem; color: #1a1d2e; }
.issue-list-cnt { background: #f3f4f6; color: #6b7280; font-size: 0.78rem; font-weight: 600; padding: 2px 8px; border-radius: 99px; margin-left: 6px; }
.issue-tabs-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  row-gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e8eaf0;
}
.issue-tabs-main {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  flex: 1 1 0;
  min-width: 0;
}
.tab-btn { height: 40px; padding: 0 16px; border: none; background: transparent; font-size: 0.85rem; color: #6b7280; cursor: pointer; transition: color 0.2s, border-color 0.2s; font-weight: 600; border-bottom: 2px solid transparent; margin-bottom: -2px; display: inline-flex; align-items: center; box-sizing: border-box; flex-shrink: 0; white-space: nowrap; }
.tab-btn:hover { color: #1A6AFF; }
.tab-btn.active { color: #1A6AFF; border-bottom-color: #1A6AFF; }
.tab-badge { display: inline-block; background: #f3f4f6; color: #6b7280; font-size: 0.7rem; padding: 2px 6px; border-radius: 99px; margin-left: 6px; font-weight: 600; }
.tab-btn.active .tab-badge { background: #dbeafe; color: #1A6AFF; }
.tab-divider { width: 1px; height: 14px; background: #e5e7eb; margin: 0 6px 0 2px; flex-shrink: 0; align-self: center; }
.urgency-group {
  display: inline-flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
  margin-left: 4px;
}
.urgency-btn {
  box-sizing: border-box;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 22px;
  min-width: 28px;
  padding: 0 10px;
  border: none;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 700;
  line-height: 1;
  color: #fff;
  cursor: pointer;
  flex-shrink: 0;
  align-self: center;
  margin-bottom: -2px;
  opacity: 0.72;
  transform: scale(1);
  transition: opacity 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}
.urgency-btn:hover,
.urgency-btn:focus-visible {
  color: #fff;
  outline: none;
  opacity: 1;
}
.urgency-btn.is-active {
  color: #fff;
  outline: none;
  opacity: 1;
  animation: urgency-active-glow 1.25s ease-in-out infinite;
}
@keyframes urgency-active-glow {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.45);
  }
  50% {
    transform: scale(1.08);
    box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.55), 0 4px 10px rgba(0, 0, 0, 0.12);
  }
}
.urgency-btn:focus-visible { box-shadow: 0 0 0 2px rgba(26, 106, 255, 0.35); }
.urgency-btn.is-active:focus-visible { animation: urgency-active-glow 1.25s ease-in-out infinite; }
.urgency-high { background: #ef4444; }
.urgency-high:hover,
.urgency-high:focus-visible,
.urgency-high.is-active { background: #ef4444; }
.urgency-medium { background: #fbbf24; }
.urgency-medium:hover,
.urgency-medium:focus-visible,
.urgency-medium.is-active { background: #fbbf24; }
.urgency-low { background: #3b82f6; }
.urgency-low:hover,
.urgency-low:focus-visible,
.urgency-low.is-active { background: #3b82f6; }
.issue-card { background: #fff; border: 1px solid #e8eaf0; border-radius: 12px; overflow: hidden; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(60,72,120,.05); transition: transform 0.2s, box-shadow 0.2s; }
.issue-card:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(60,72,120,.08); }
.issue-card-row { display: flex; }
.issue-thumb { width: 200px; background: #f3f4f6; position: relative; display: flex; align-items: center; justify-content: center; cursor: pointer; overflow: hidden; flex-shrink: 0; }
.thumb-mode-badge { position: absolute; top: 8px; right: 8px; font-size: 0.6rem; background: rgba(0,0,0,.6); color: #fff; padding: 2px 8px; border-radius: 4px; font-weight: 600; z-index: 10; }
.real-thumb-crop { width: 100%; height: 100%; position: absolute; inset: 0; background-repeat: no-repeat; z-index: 1; }
.real-thumb-box { position: absolute; border: 2px solid #ef4444; background: rgba(239,68,68,0.15); box-shadow: 0 0 0 2000px rgba(0,0,0,0.35); border-radius: 2px; }
.issue-thumb-inner { width: 78%; display: flex; gap: 6px; z-index: 5; }
.tb { height: 30px; border-radius: 5px; }
.tb-light { background: rgba(255,255,255,.55); flex: 1; }
.tb-red { border: 2px solid rgba(239,68,68,.8); background: rgba(239,68,68,.08); flex: 1.5; }
.issue-thumb-footer { position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,.5); color: #fff; font-size: 0.7rem; text-align: center; padding: 5px 0; z-index: 10; }
.issue-thumb:hover .issue-thumb-footer { background: rgba(26, 106, 255,.8); }
.preview-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.6); z-index: 9999; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(4px); }
.preview-modal { background: #fff; border-radius: 14px; max-width: 80vw; max-height: 85vh; overflow: hidden; box-shadow: 0 24px 50px rgba(0,0,0,.3); display: flex; flex-direction: column; }
.preview-header { display: flex; align-items: center; gap: 12px; padding: 16px 20px; border-bottom: 1px solid #e8eaf0; }
.preview-mode-badge { font-size: 0.7rem; background: #1A6AFF; color: #fff; padding: 3px 10px; border-radius: 4px; font-weight: 600; }
.preview-title { font-weight: 700; font-size: 1rem; color: #1a1d2e; flex: 1; }
.preview-close { background: none; border: none; font-size: 1.1rem; cursor: pointer; color: #9ca3af; padding: 4px 8px; border-radius: 4px; }
.preview-close:hover { background: #f3f4f6; color: #1a1d2e; }
.preview-body { overflow: auto; padding: 20px; display: flex; justify-content: center; background: #f4f6fb; }
.preview-crop { position: relative; background-repeat: no-repeat; border-radius: 8px; border: 1px solid #e8eaf0; flex-shrink: 0; }
.preview-box { position: absolute; border: 2px solid #ef4444; background: rgba(239,68,68,0.12); box-shadow: 0 0 0 2000px rgba(0,0,0,0.25); border-radius: 2px; }
.preview-empty { padding: 60px; text-align: center; color: #9ca3af; }
.preview-footer { padding: 14px 20px; border-top: 1px solid #e8eaf0; display: flex; align-items: center; gap: 12px; }
.preview-desc { font-size: 0.85rem; color: #6b7280; }
.issue-body { flex: 1; padding: 20px 24px; display: flex; flex-direction: column; gap: 8px; }
.issue-badge-row { display: flex; align-items: center; gap: 12px; }
.issue-badge { display: inline-flex; align-items: center; gap: 4px; font-size: 0.7rem; font-weight: 800; padding: 3px 10px; border-radius: 4px; letter-spacing: .04em; color: white; }
.badge-high { background: #ef4444; }
.badge-medium { background: #fbbf24; color: #fff; }
.badge-low { background: #3b82f6; }
.issue-assignee { font-size: 0.78rem; color: #9ca3af; font-weight: 500; }
.issue-tag { font-size: 0.7rem; font-weight: 600; padding: 2px 8px; border-radius: 4px; white-space: nowrap; }
.issue-title { font-weight: 700; font-size: 1rem; color: #1a1d2e; }
.issue-desc { font-size: 0.85rem; color: #6b7280; line-height: 1.6; }
.issue-fix { background: #f8faff; border-left: 3px solid #1A6AFF; padding: 10px 14px; margin-top: 4px; border-radius: 0 6px 6px 0; }
.issue-fix-label { font-size: 0.75rem; color: #1A6AFF; font-weight: 700; margin-bottom: 4px; }
.issue-fix-text { font-size: 0.8rem; font-family: monospace; color: #4b5563; }

.ignore-btn {
  margin-left: auto;
  padding: 0 10px;
  height: 26px;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  background: #f9fafb;
  color: #6b7280;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  display: inline-flex;
  align-items: center;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
}
.issue-card:hover .ignore-btn { opacity: 1; pointer-events: auto; }
.ignore-btn:hover { background: #eef2ff; color: #1A6AFF; border-color: #93b4fd; }
.ignore-btn--restore { opacity: 1; pointer-events: auto; }
.ignore-btn--restore:hover { background: #dbeafe; color: #1d4ed8; border-color: #93c5fd; }
.issue-card--ignored { opacity: 0.55; }

.ignored-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  margin-left: auto;
  font-size: 0.8rem;
  white-space: nowrap;
}
.ignored-hint { color: #9ca3af; }
.ignored-toggle, .ignored-restore-all {
  padding: 0 8px;
  height: 26px;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  background: #f9fafb;
  color: #6b7280;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
}
.ignored-toggle:hover { background: #eef2ff; color: #4338ca; border-color: #a5b4fc; }
.ignored-restore-all:hover { background: #dbeafe; color: #1d4ed8; border-color: #93c5fd; }
.ignored-section { margin-top: 16px; }
.ignored-section-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: #9ca3af;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px dashed #e5e7eb;
}

.empty-state { text-align: center; padding: 40px; color: #9ca3af; background: white; border-radius: 12px; border: 1px solid #e8eaf0; }
.issue-pagination { margin-top: 8px; padding: 16px 18px; background: #fff; border: 1px solid #e8eaf0; border-radius: 12px; box-shadow: 0 1px 3px rgba(60,72,120,.05); }
.pagination-row { display: flex; flex-wrap: wrap; align-items: center; gap: 14px 20px; font-size: 0.82rem; color: #6b7280; }
.pagination-total { font-weight: 600; color: #4b5563; }
.pagination-size { display: inline-flex; align-items: center; gap: 6px; cursor: pointer; }
.pagination-select { border: 1px solid #e8eaf0; border-radius: 6px; height: 32px; padding: 0 28px 0 10px; font-size: 0.82rem; font-family: inherit; color: #1a1d2e; background: #fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%236b7280' d='M3 4.5L6 7.5L9 4.5'/%3E%3C/svg%3E") no-repeat right 8px center; cursor: pointer; appearance: none; box-sizing: border-box; }
.pagination-select:hover { border-color: #c7d2fe; }
.pagination-nav { display: inline-flex; align-items: center; gap: 10px; }
.pagination-pages { font-weight: 600; color: #1a1d2e; min-width: 7em; text-align: center; }
.pagination-btn { border: 1px solid #e8eaf0; background: #fff; border-radius: 6px; height: 32px; padding: 0 12px; font-size: 0.8rem; font-weight: 600; color: #4b5563; cursor: pointer; font-family: inherit; transition: border-color 0.15s, color 0.15s; display: inline-flex; align-items: center; box-sizing: border-box; }
.pagination-btn:hover:not(:disabled) { border-color: #1A6AFF; color: #1A6AFF; }
.pagination-btn:disabled { opacity: 0.45; cursor: not-allowed; }
.pagination-btn-go { background: #1A6AFF; border-color: #1A6AFF; color: #fff; }
.pagination-btn-go:hover:not(:disabled) { background: #1557e6; border-color: #1557e6; color: #fff; }
.pagination-jump { display: inline-flex; align-items: center; gap: 8px; margin-left: auto; }
.pagination-jump-lbl { white-space: nowrap; }
.pagination-input { width: 52px; height: 32px; border: 1px solid #e8eaf0; border-radius: 6px; padding: 0 8px; font-size: 0.82rem; text-align: center; font-family: inherit; box-sizing: border-box; }
.pagination-input:focus { outline: none; border-color: #1A6AFF; box-shadow: 0 0 0 2px rgba(26, 106, 255, 0.15); }
@media (max-width: 720px) {
  .pagination-jump { margin-left: 0; width: 100%; }
}
.rpt-sidebar { display: flex; flex-direction: column; min-height: 0; height: 100%; }
.meta-card { background: #fff; border: 1px solid #e8eaf0; border-radius: 14px; box-shadow: 0 1px 4px rgba(60,72,120,.06); overflow: hidden; }
.meta-card-hd { padding: 14px 20px; font-weight: 700; font-size: 0.9rem; background: #fafbff; border-bottom: 1px solid #f0f1f6; color: #1a1d2e; }
.meta-row { display: flex; justify-content: space-between; padding: 12px 20px; border-bottom: 1px solid #f4f5f9; font-size: 0.85rem; }
.meta-row:last-child { border-bottom: none; }
.meta-lbl { color: #9ca3af; }
.meta-val { font-weight: 600; text-align: right; color: #4b5563; }
.meta-val a { color: #1A6AFF; text-decoration: none; }
.snapshot-card { padding: 15px; margin-top: 15px; }
.snapshot-title { font-weight: bold; font-size: 0.84rem; margin-bottom: 10px; }
.snapshot-img { width: 100%; border: 1px solid #e8eaf0; border-radius: 8px; cursor: pointer; }
.snapshot-placeholder { padding: 40px 10px; text-align: center; background: #f9fafb; color: #9ca3af; font-size: 0.8rem; border-radius: 8px; border: 1px dashed #e8eaf0; }
.help-card { background: #1A6AFF; border-radius: 14px; padding: 20px; color: #fff; margin-top: 15px; }
.help-title { font-weight: 700; font-size: 0.95rem; margin-bottom: 8px; }
.help-desc { font-size: 0.8rem; opacity: .92; margin-bottom: 16px; line-height: 1.55; }
.help-btn-wrap { position: relative; display: inline-block; width: 100%; }
.help-btn { width: 100%; height: 36px; padding: 0; border-radius: 8px; background: rgba(255,255,255,.2); border: 1px solid rgba(255,255,255,.3); color: #fff; cursor: pointer; font-size: 0.85rem; font-weight: 600; display: flex; align-items: center; justify-content: center; box-sizing: border-box; }
.help-btn:hover { background: rgba(255,255,255,.3); }
.help-tooltip { position: absolute; bottom: 100%; left: 50%; transform: translateX(-50%); background: #1a1d2e; color: white; padding: 8px 12px; border-radius: 6px; font-size: 0.75rem; opacity: 0; visibility: hidden; transition: all 0.2s ease; white-space: nowrap; margin-bottom: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); pointer-events: none; z-index: 10; font-weight: 500; }
.help-tooltip::after { content: ''; position: absolute; top: 100%; left: 50%; transform: translateX(-50%); border-width: 5px; border-style: solid; border-color: #1a1d2e transparent transparent transparent; }
.help-btn-wrap:hover .help-tooltip { opacity: 1; visibility: visible; margin-bottom: 12px; }
.trend-card { background: #fff; border: 1px solid #e8eaf0; border-radius: 14px; padding: 20px; box-shadow: 0 1px 4px rgba(60,72,120,.06); margin-top: 15px; }
.trend-title { font-size: 0.9rem; font-weight: 700; color: #1a1d2e; margin-bottom: 18px; }
.trend-chart { display: flex; align-items: flex-end; gap: 10px; height: 80px; }
.bar-wrap { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px; justify-content: flex-end; }
.bar-fill { width: 100%; border-radius: 4px 4px 0 0; background: #dbeafe; transition: height 0.5s ease; min-height: 4px; }
.bar-fill.today { background: #1A6AFF; }
.bar-val { font-size: 0.7rem; font-weight: 800; order: -1; }
.bar-date { font-size: 0.65rem; color: #9ca3af; font-weight: 500; }
.trend-empty { font-size: 0.8rem; color: #9ca3af; text-align: center; padding: 15px 0; }
.loading-state { padding: 100px; text-align: center; }
@media (max-width: 900px) {
  .rpt-top-row { grid-template-columns: 1fr; }
  .rpt-left-stack { height: auto; }
  .distribution-card { flex: 0 1 auto; }
}
@media print {
  .no-print { display: none !important; }
  .rpt-body { background: white !important; }
  .rpt-page { padding-top: 0 !important; }
  .rpt-card { box-shadow: none !important; border: 1px solid #ddd !important; }
}
</style>
