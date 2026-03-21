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

        <div class="rpt-layout">
          <div id="left-col">
            <div class="rpt-card score-card">
              <div class="score-card-hdg">设计还原度评分（{{ currentModeName }}）</div>
              <div class="score-body">
                <div class="ring-wrap">
                  <svg class="ring-svg" width="110" height="110" viewBox="0 0 110 110">
                    <circle class="ring-bg" cx="55" cy="55" r="44" />
                    <circle class="ring-fg" cx="55" cy="55" r="44"
                      :stroke-dashoffset="276.5 - (276.5 * (reportData.score || 0) / 100)"
                      stroke-dasharray="276.5" />
                  </svg>
                  <div class="ring-label">
                    <span class="ring-pct">{{ reportData.score || 0 }}%</span>
                    <span class="ring-sub">还原度</span>
                  </div>
                </div>
                <div class="score-detail">
                  <div class="score-badge" :class="scoreBadgeClass">{{ scoreBadgeText }}</div>
                  <div class="score-desc">本次走查发现 {{ reportData.issueCount || 0 }} 个规范问题。建议优先修复高优问题。</div>
                  <div class="score-stats">
                    <div v-if="isDesignMode" class="stat-block">
                      <div class="stat-val">{{ dimensionScores.content }}%</div>
                      <div class="stat-label">内容契合度</div>
                    </div>
                    <div class="stat-block">
                      <div class="stat-val">{{ dimensionScores.visual }}%</div>
                      <div class="stat-label">视觉一致性</div>
                    </div>
                    <div class="stat-block">
                      <div class="stat-val">{{ dimensionScores.interaction }}%</div>
                      <div class="stat-label">交互匹配度</div>
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
                    <div class="chart-bar-wrap">
                      <div class="chart-bar" :style="{ width: item.percentage + '%', background: item.color }"></div>
                    </div>
                    <div class="chart-info">
                      <span class="chart-label">{{ item.name }}</span>
                      <span class="chart-count">{{ item.count }} 个问题 ({{ item.percentage }}%)</span>
                    </div>
                  </div>
                </div>
                <div class="distribution-summary">
                  <div class="summary-label">AI 问题总结</div>
                  <div class="summary-text">{{ reportData.diagnosis || '暂无 AI 总结' }}</div>
                </div>
              </div>
            </div>

            <div>
              <div class="issue-list-hd">
                <div class="issue-list-title">关键问题清单 <span class="issue-list-cnt">{{ filteredIssues.length }}</span></div>
              </div>
              <div class="issue-tabs no-print">
                <button class="tab-btn" :class="{ active: activeTab === 'all' }" @click="activeTab = 'all'">
                  全部问题 <span class="tab-badge">{{ allIssues.length }}</span>
                </button>
                <button class="tab-btn" :class="{ active: activeTab === 'visual' }" @click="activeTab = 'visual'">
                  视觉一致性 <span class="tab-badge">{{ visualIssues.length }}</span>
                </button>
                <button class="tab-btn" :class="{ active: activeTab === 'interaction' }" @click="activeTab = 'interaction'">
                  交互体验 <span class="tab-badge">{{ interactionIssues.length }}</span>
                </button>
                <button class="tab-btn" :class="{ active: activeTab === 'content' }" @click="activeTab = 'content'">
                  文案与话术 <span class="tab-badge">{{ contentIssues.length }}</span>
                </button>
              </div>

              <div class="issue-card" v-for="issue in filteredIssues" :key="issue.id">
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
                      <span class="issue-badge" :class="issue.level === 'high' ? 'badge-critical' : 'badge-warning'">
                        {{ issue.level === 'high' ? 'CRITICAL' : 'WARNING' }}
                      </span>
                      <span class="issue-tag" :style="{ background: getIssueTag(issue).bg, color: getIssueTag(issue).color }">{{ getIssueTag(issue).label }}</span>
                      <span class="issue-assignee">{{ getCategoryLabel(issue.category) }}</span>
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
                <span class="meta-lbl">基准模式</span>
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
              <div class="help-desc">如果走查结果存在误报，您可以手动标记该条目为已忽略。</div>
              <div class="help-btn-wrap">
                <button class="help-btn">反馈问题</button>
                <div class="help-tooltip">此功能开发中，敬请期待</div>
              </div>
            </div>

            <div class="trend-card no-print">
              <div class="trend-title">近期历史还原度趋势</div>
              <div class="trend-chart" v-if="trendData.length > 0">
                <div class="bar-wrap" v-for="(item, idx) in trendData" :key="idx">
                  <div class="bar-val" :style="{ color: idx === trendData.length - 1 ? '#3b6ef8' : '#9ca3af' }">{{ item.score }}%</div>
                  <div class="bar-fill" :class="{ today: idx === trendData.length - 1 }" :style="'height:' + Math.max(item.score * 0.6, 10) + 'px'"></div>
                  <div class="bar-date">{{ item.date }}</div>
                </div>
              </div>
              <div v-else class="trend-empty">暂无足够历史数据</div>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppNavbar from '../components/AppNavbar.vue'
import { useAuditStore } from '../store/audit'
import { useUserStore } from '../store/user'
import axios from 'axios'

const router = useRouter()
const auditStore = useAuditStore()
const userStore = useUserStore()
const reportData = auditStore.reportData

const activeTab = ref('all')
const trendData = ref([])
const previewIssue = ref(null)

const categoryMapping = {
  visual: ['视觉', '排版规范', '按钮规范', '表单规范', '导航规范', '展示规范', '间距规范'],
  interaction: ['交互', '布局', '无障碍'],
  content: ['质量', '性能与质量', '文案', '话术']
}

const getCategoryType = (category) => {
  if (!category) return 'visual'
  for (const [type, keywords] of Object.entries(categoryMapping)) {
    if (keywords.some(kw => category.includes(kw))) return type
  }
  return 'visual'
}

const getCategoryLabel = (category) => {
  const labels = { visual: '视觉一致性', interaction: '交互体验', content: '文案与话术' }
  return labels[getCategoryType(category)] || category
}

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
  const text = ((issue.title || '') + (issue.category || '')).toLowerCase()
  for (const rule of issueTagMap) {
    if (rule.keywords.some(kw => text.includes(kw))) {
      return rule
    }
  }
  return { label: '样式', bg: '#f3f4f6', color: '#6b7280' }
}

const isDesignMode = computed(() => auditStore.checkMode === 'design')

const currentModeName = computed(() => {
  return auditStore.checkMode === 'baseline' ? '基准值模式' : '设计稿模式'
})

const scoreBadgeClass = computed(() => {
  const s = reportData ? reportData.score : 0
  if (s >= 90) return 'badge-good'
  if (s >= 70) return 'badge-ok'
  return 'badge-bad'
})

const scoreBadgeText = computed(() => {
  const s = reportData ? reportData.score : 0
  if (s >= 90) return '表现优秀，基本符合规范'
  if (s >= 70) return '存在部分偏差，建议修复'
  return '偏离度较高，需重点整改'
})

const allIssues = computed(() => reportData && reportData.issues ? reportData.issues : [])

const visualIssues = computed(() => allIssues.value.filter(i => getCategoryType(i.category) === 'visual'))
const interactionIssues = computed(() => allIssues.value.filter(i => getCategoryType(i.category) === 'interaction'))
const contentIssues = computed(() => allIssues.value.filter(i => getCategoryType(i.category) === 'content'))

const filteredIssues = computed(() => {
  if (activeTab.value === 'visual') return visualIssues.value
  if (activeTab.value === 'interaction') return interactionIssues.value
  if (activeTab.value === 'content') return contentIssues.value
  return allIssues.value
})

const dimensionScores = computed(() => {
  const calc = (issues) => {
    const h = issues.filter(i => i.level === 'high').length
    const m = issues.filter(i => i.level === 'medium').length
    const l = issues.filter(i => i.level === 'low' || i.level === 'warning').length
    return Math.max(0, 100 - (h * 8 + m * 3 + l * 1))
  }
  return {
    content: calc(contentIssues.value),
    visual: calc(visualIssues.value),
    interaction: calc(interactionIssues.value)
  }
})

const topIssueCategories = computed(() => {
  const counts = {}
  allIssues.value.forEach(i => {
    const t = getCategoryType(i.category)
    counts[t] = (counts[t] || 0) + 1
  })
  const total = allIssues.value.length || 1
  const cats = [
    { name: '视觉一致性', key: 'visual', color: '#3b6ef8' },
    { name: '交互体验', key: 'interaction', color: '#f59e0b' },
    { name: '文案与话术', key: 'content', color: '#10b981' }
  ]
  return cats
    .map(c => ({
      name: c.name,
      count: counts[c.key] || 0,
      percentage: Math.round(((counts[c.key] || 0) / total) * 100),
      color: c.color
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 3)
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
.rpt-breadcrumb a:hover { color: #3b6ef8; }
.rpt-breadcrumb .cur { color: #1a1d2e; font-weight: 500; }
.rpt-layout { display: grid; grid-template-columns: 1fr 300px; gap: 20px; align-items: flex-start; }
.btn { border: none; font-family: inherit; cursor: pointer; transition: all 0.2s; font-weight: 600; }
.btn-primary { background: #3b6ef8; color: white; border-radius: 6px; padding: 8px 16px; font-size: 0.85rem; }
.btn-primary:hover { background: #256af4; }
.btn-ghost { background: transparent; color: #6b7280; border: 1px solid #e8eaf0; border-radius: 6px; padding: 8px 16px; font-size: 0.85rem; }
.btn-ghost:hover { background: #f9fafb; color: #1a1d2e; }
.rpt-card { background: #fff; border: 1px solid #e8eaf0; border-radius: 14px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(60,72,120,.04); overflow: hidden; }
.score-card { padding: 22px 24px; }
.score-card-hdg { font-size: 1rem; font-weight: 700; color: #1a1d2e; margin-bottom: 20px; }
.score-body { display: flex; align-items: flex-start; gap: 28px; }
.ring-wrap { position: relative; width: 110px; height: 110px; flex-shrink: 0; }
.ring-svg { transform: rotate(-90deg); }
.ring-bg { fill: none; stroke: #eef2ff; stroke-width: 10; }
.ring-fg { fill: none; stroke: #3b6ef8; stroke-width: 10; stroke-linecap: round; transition: stroke-dashoffset 1s ease; }
.ring-label { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.ring-pct { font-size: 1.6rem; font-weight: 800; color: #3b6ef8; line-height: 1; }
.ring-sub { font-size: 0.68rem; color: #9ca3af; margin-top: 3px; }
.score-detail { flex: 1; }
.score-badge { display: inline-flex; padding: 4px 12px; border-radius: 99px; font-size: 0.78rem; font-weight: 600; margin-bottom: 12px; }
.badge-good { background: #d1fae5; color: #065f46; }
.badge-ok { background: #fef3c7; color: #92400e; }
.badge-bad { background: #fee2e2; color: #991b1b; }
.score-desc { font-size: 0.86rem; color: #6b7280; line-height: 1.75; margin-bottom: 18px; }
.score-stats { display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; }
.stat-block { flex: 1; min-width: 80px; }
.stat-val { font-size: 1.2rem; font-weight: 800; color: #1a1d2e; }
.stat-label { font-size: 0.75rem; color: #9ca3af; margin-top: 4px; }
.distribution-card { padding: 22px 24px; }
.distribution-hd { font-size: 1rem; font-weight: 700; color: #1a1d2e; margin-bottom: 18px; }
.distribution-body { display: flex; flex-direction: column; gap: 20px; }
.distribution-chart { display: flex; flex-direction: column; gap: 12px; }
.chart-item { display: flex; flex-direction: column; gap: 6px; }
.chart-bar-wrap { width: 100%; height: 8px; background: #f3f4f6; border-radius: 4px; overflow: hidden; }
.chart-bar { height: 100%; border-radius: 4px; transition: width 0.5s ease; }
.chart-info { display: flex; justify-content: space-between; align-items: center; }
.chart-label { font-size: 0.85rem; font-weight: 600; color: #1a1d2e; }
.chart-count { font-size: 0.8rem; color: #6b7280; }
.distribution-summary { background: #f8faff; border-left: 3px solid #3b6ef8; padding: 14px 16px; border-radius: 0 8px 8px 0; }
.summary-label { font-size: 0.75rem; color: #3b6ef8; font-weight: 700; margin-bottom: 8px; }
.summary-text { font-size: 0.85rem; color: #4b5563; line-height: 1.6; }
.issue-list-hd { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.issue-list-title { font-weight: 700; font-size: 1rem; color: #1a1d2e; }
.issue-list-cnt { background: #f3f4f6; color: #6b7280; font-size: 0.78rem; font-weight: 600; padding: 2px 8px; border-radius: 99px; margin-left: 6px; }
.issue-tabs { display: flex; gap: 8px; margin-bottom: 16px; border-bottom: 2px solid #e8eaf0; }
.tab-btn { padding: 10px 16px; border: none; background: transparent; font-size: 0.85rem; color: #6b7280; cursor: pointer; transition: all 0.2s; font-weight: 600; border-bottom: 2px solid transparent; margin-bottom: -2px; }
.tab-btn:hover { color: #3b6ef8; }
.tab-btn.active { color: #3b6ef8; border-bottom-color: #3b6ef8; }
.tab-badge { display: inline-block; background: #f3f4f6; color: #6b7280; font-size: 0.7rem; padding: 2px 6px; border-radius: 99px; margin-left: 6px; font-weight: 600; }
.tab-btn.active .tab-badge { background: #dbeafe; color: #3b6ef8; }
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
.issue-thumb:hover .issue-thumb-footer { background: rgba(59,110,248,.8); }
.preview-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.6); z-index: 9999; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(4px); }
.preview-modal { background: #fff; border-radius: 14px; max-width: 80vw; max-height: 85vh; overflow: hidden; box-shadow: 0 24px 50px rgba(0,0,0,.3); display: flex; flex-direction: column; }
.preview-header { display: flex; align-items: center; gap: 12px; padding: 16px 20px; border-bottom: 1px solid #e8eaf0; }
.preview-mode-badge { font-size: 0.7rem; background: #3b6ef8; color: #fff; padding: 3px 10px; border-radius: 4px; font-weight: 600; }
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
.badge-critical { background: #ef4444; }
.badge-warning { background: #f59e0b; }
.issue-assignee { font-size: 0.78rem; color: #9ca3af; margin-left: auto; font-weight: 500; }
.issue-tag { font-size: 0.7rem; font-weight: 600; padding: 2px 8px; border-radius: 4px; white-space: nowrap; }
.issue-title { font-weight: 700; font-size: 1rem; color: #1a1d2e; }
.issue-desc { font-size: 0.85rem; color: #6b7280; line-height: 1.6; }
.issue-fix { background: #f8faff; border-left: 3px solid #3b6ef8; padding: 10px 14px; margin-top: 4px; border-radius: 0 6px 6px 0; }
.issue-fix-label { font-size: 0.75rem; color: #3b6ef8; font-weight: 700; margin-bottom: 4px; }
.issue-fix-text { font-size: 0.8rem; font-family: monospace; color: #4b5563; }
.empty-state { text-align: center; padding: 40px; color: #9ca3af; background: white; border-radius: 12px; border: 1px solid #e8eaf0; }
.rpt-sidebar { display: flex; flex-direction: column; }
.meta-card { background: #fff; border: 1px solid #e8eaf0; border-radius: 14px; box-shadow: 0 1px 4px rgba(60,72,120,.06); overflow: hidden; }
.meta-card-hd { padding: 14px 20px; font-weight: 700; font-size: 0.9rem; background: #fafbff; border-bottom: 1px solid #f0f1f6; color: #1a1d2e; }
.meta-row { display: flex; justify-content: space-between; padding: 12px 20px; border-bottom: 1px solid #f4f5f9; font-size: 0.85rem; }
.meta-row:last-child { border-bottom: none; }
.meta-lbl { color: #9ca3af; }
.meta-val { font-weight: 600; text-align: right; color: #4b5563; }
.meta-val a { color: #3b6ef8; text-decoration: none; }
.snapshot-card { padding: 15px; margin-top: 15px; }
.snapshot-title { font-weight: bold; font-size: 0.84rem; margin-bottom: 10px; }
.snapshot-img { width: 100%; border: 1px solid #e8eaf0; border-radius: 8px; cursor: pointer; }
.snapshot-placeholder { padding: 40px 10px; text-align: center; background: #f9fafb; color: #9ca3af; font-size: 0.8rem; border-radius: 8px; border: 1px dashed #e8eaf0; }
.help-card { background: #3b6ef8; border-radius: 14px; padding: 20px; color: #fff; margin-top: 15px; }
.help-title { font-weight: 700; font-size: 0.95rem; margin-bottom: 8px; }
.help-desc { font-size: 0.8rem; opacity: .9; margin-bottom: 16px; line-height: 1.5; }
.help-btn-wrap { position: relative; display: inline-block; width: 100%; }
.help-btn { width: 100%; padding: 10px; border-radius: 8px; background: rgba(255,255,255,.2); border: 1px solid rgba(255,255,255,.3); color: #fff; cursor: pointer; font-size: 0.85rem; font-weight: 600; }
.help-btn:hover { background: rgba(255,255,255,.3); }
.help-tooltip { position: absolute; bottom: 100%; left: 50%; transform: translateX(-50%); background: #1a1d2e; color: white; padding: 8px 12px; border-radius: 6px; font-size: 0.75rem; opacity: 0; visibility: hidden; transition: all 0.2s ease; white-space: nowrap; margin-bottom: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); pointer-events: none; z-index: 10; font-weight: 500; }
.help-tooltip::after { content: ''; position: absolute; top: 100%; left: 50%; transform: translateX(-50%); border-width: 5px; border-style: solid; border-color: #1a1d2e transparent transparent transparent; }
.help-btn-wrap:hover .help-tooltip { opacity: 1; visibility: visible; margin-bottom: 12px; }
.trend-card { background: #fff; border: 1px solid #e8eaf0; border-radius: 14px; padding: 20px; box-shadow: 0 1px 4px rgba(60,72,120,.06); margin-top: 15px; }
.trend-title { font-size: 0.9rem; font-weight: 700; color: #1a1d2e; margin-bottom: 18px; }
.trend-chart { display: flex; align-items: flex-end; gap: 10px; height: 80px; }
.bar-wrap { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px; justify-content: flex-end; }
.bar-fill { width: 100%; border-radius: 4px 4px 0 0; background: #dbeafe; transition: height 0.5s ease; min-height: 4px; }
.bar-fill.today { background: #3b6ef8; }
.bar-val { font-size: 0.7rem; font-weight: 800; order: -1; }
.bar-date { font-size: 0.65rem; color: #9ca3af; font-weight: 500; }
.trend-empty { font-size: 0.8rem; color: #9ca3af; text-align: center; padding: 15px 0; }
.loading-state { padding: 100px; text-align: center; }
@media print {
  .no-print { display: none !important; }
  .rpt-body { background: white !important; }
  .rpt-page { padding-top: 0 !important; }
  .rpt-card { box-shadow: none !important; border: 1px solid #ddd !important; }
}
</style>
