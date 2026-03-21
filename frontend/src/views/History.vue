<template>
  <div class="history-page">
    <AppNavbar variant="full" active-key="history" />

    <div class="container" style="margin-top: 40px;">
      <div class="page-header">
        <h2 class="page-title">🕐 历史走查记录</h2>
        <p class="page-desc">查看和管理过往的 UI 审计报告与走查分析结果</p>
      </div>

      <div v-if="loading" class="state-container">
        <div class="spinner"></div>
        <p style="margin-top:12px;">正在加载真实历史数据...</p>
      </div>
      
      <div v-else-if="historyList.length === 0" class="state-container empty-state">
        <div style="font-size: 40px; margin-bottom: 10px; opacity: 0.5;">📭</div>
        <p>暂无走查记录</p>
        <button class="btn btn-primary" style="margin-top: 15px;" @click="goTo('/')">去发起第一次走查</button>
      </div>

      <template v-else>
        <div class="filters-wrap">
          <div class="filters-row top-row">
            <div class="filter-item search-item">
              <label>网址搜索</label>
              <input
                v-model.trim="searchKeyword"
                class="search-input"
                placeholder="按走查网址搜索，例如：example.com"
              />
            </div>
            <div class="filter-item">
              <label>走查模式</label>
              <select v-model="selectedMode" class="filter-select">
                <option value="all">全部模式</option>
                <option value="baseline">基准值模式</option>
                <option value="design">设计稿模式</option>
                <option value="component">组件模式</option>
              </select>
            </div>
            <div class="filter-item">
              <label>问题类型</label>
              <select v-model="selectedIssueType" class="filter-select">
                <option value="all">全部问题类型</option>
                <option value="visual">视觉一致性</option>
                <option value="interaction">交互体验</option>
                <option value="content">文案与话术</option>
              </select>
            </div>
          </div>

          <div class="filters-row">
            <div class="filter-item date-range-item">
              <label>走查日期</label>
              <div class="date-range-group">
                <input type="date" v-model="startDate" class="date-input" />
                <span class="date-sep">至</span>
                <input type="date" v-model="endDate" class="date-input" />
              </div>
            </div>
            <div class="result-tip">当前结果：<strong>{{ filteredHistoryList.length }}</strong> 条</div>
            <button class="btn btn-light" @click="resetFilters">重置筛选</button>
          </div>

          <div class="filters-row slider-row">
            <div class="slider-label">
              问题数量筛选：{{ issueCountRange[0] }} - {{ issueCountRange[1] }}
            </div>
            <div class="slider-group">
              <input
                type="range"
                :min="0"
                :max="maxIssueCount"
                v-model.number="issueCountRange[0]"
                @input="normalizeIssueRange('min')"
              />
              <input
                type="range"
                :min="0"
                :max="maxIssueCount"
                v-model.number="issueCountRange[1]"
                @input="normalizeIssueRange('max')"
              />
            </div>
          </div>

          <div class="actions-row">
            <label class="check-all">
              <input
                type="checkbox"
                :checked="allVisibleSelected"
                @change="toggleSelectAllVisible"
              />
              <span>全选当前筛选结果（{{ filteredHistoryList.length }}）</span>
            </label>
            <button
              class="btn btn-danger"
              :disabled="selectedIds.length === 0 || deleting"
              @click="deleteSelected"
            >
              {{ deleting ? '删除中...' : `删除选中（${selectedIds.length}）` }}
            </button>
          </div>
        </div>

        <div v-if="filteredHistoryList.length === 0" class="state-container empty-state">
          <div style="font-size: 36px; margin-bottom: 10px; opacity: 0.6;">🔎</div>
          <p>未找到匹配的历史记录，请调整筛选条件</p>
        </div>

        <div v-else class="project-grid">
          <div class="project-card" v-for="item in filteredHistoryList" :key="item.id" @click="viewReport(item)">
            <div class="card-check">
              <input
                type="checkbox"
                :checked="selectedIds.includes(item.id)"
                @click.stop
                @change="toggleSelect(item.id)"
              />
            </div>
            <div class="project-thumb" style="background: linear-gradient(135deg, #e8ecf5, #d4daea)">
               <div class="score-display">{{ item.score || 0 }}<span style="font-size:1.2rem;">%</span></div>
               <span class="mode-badge">{{ modeLabel(item.mode) }}</span>
            </div>
            <div class="project-info">
              <div class="project-name" :title="item.url">{{ formatUrl(item.url) }}</div>
              <div class="project-time">🕐 {{ item.created_at || '未知时间' }}</div>
              <div class="project-meta">发现问题: <strong style="color:#ef4444">{{ item.issue_count || 0 }}</strong> 项</div>
              <div class="project-tags">
                <span v-for="type in getItemIssueTypes(item)" :key="type" class="type-tag">{{ issueTypeLabel(type) }}</span>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import AppNavbar from '../components/AppNavbar.vue'
import { useUserStore } from '../store/user'
import { useAuditStore } from '../store/audit'
import axios from 'axios'

const router = useRouter()
const userStore = useUserStore()
const auditStore = useAuditStore()

const historyList = ref([])
const loading = ref(true)
const deleting = ref(false)

const searchKeyword = ref('')
const selectedMode = ref('all')
const startDate = ref('')
const endDate = ref('')
const selectedIssueType = ref('all')
const issueCountRange = ref([0, 0])
const selectedIds = ref([])

const issueTypeMapping = {
  visual: ['视觉', '排版规范', '按钮规范', '表单规范', '导航规范', '展示规范', '间距规范', '像素级对比'],
  interaction: ['交互', '布局', '无障碍'],
  content: ['质量', '性能与质量', '文案', '话术']
}

onMounted(async () => {
  if (!userStore.userInfo) {
    router.push('/login')
    return
  }

  try {
    const res = await axios.get(`http://localhost:8000/api/history/${userStore.userInfo.id}`)
    if (res.data.status === 'success') {
      historyList.value = res.data.data
      issueCountRange.value = [0, maxIssueCount.value]
    }
  } catch (error) {
    console.error("加载历史记录失败", error)
  } finally {
    loading.value = false
  }
})

const getCategoryType = (category) => {
  if (!category) return 'visual'
  for (const [type, keywords] of Object.entries(issueTypeMapping)) {
    if (keywords.some(kw => String(category).includes(kw))) return type
  }
  return 'visual'
}

const getItemIssueTypes = (item) => {
  let report = item.report_data
  if (typeof item.report_data === 'string') {
    try {
      report = JSON.parse(item.report_data)
    } catch (e) {
      report = null
    }
  }
  const issues = Array.isArray(report?.issues) ? report.issues : []
  const typeSet = new Set()
  issues.forEach(issue => typeSet.add(getCategoryType(issue.category)))
  if (typeSet.size === 0) typeSet.add('visual')
  return Array.from(typeSet)
}

const issueTypeLabel = (type) => {
  const map = {
    visual: '视觉一致性',
    interaction: '交互体验',
    content: '文案与话术'
  }
  return map[type] || type
}

const modeLabel = (mode) => {
  const map = {
    baseline: '规范基准',
    design: '设计稿对比',
    component: '组件规范',
    static_scan: '规范基准'
  }
  return map[mode] || '其他模式'
}

const maxIssueCount = computed(() => {
  if (!historyList.value.length) return 0
  return Math.max(...historyList.value.map(item => Number(item.issue_count || 0)), 0)
})

watch(maxIssueCount, (maxVal) => {
  if (issueCountRange.value[1] > maxVal) {
    issueCountRange.value = [Math.min(issueCountRange.value[0], maxVal), maxVal]
  }
})

const normalizeIssueRange = (side) => {
  const [minVal, maxVal] = issueCountRange.value
  if (side === 'min' && minVal > maxVal) {
    issueCountRange.value = [maxVal, maxVal]
  } else if (side === 'max' && maxVal < minVal) {
    issueCountRange.value = [minVal, minVal]
  }
}

const toDateString = (createdAt) => {
  if (!createdAt) return ''
  const d = new Date(String(createdAt).replace(' ', 'T'))
  if (Number.isNaN(d.getTime())) return ''
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

watch([startDate, endDate], ([start, end]) => {
  if (start && end && start > end) {
    endDate.value = start
  }
})

const inDateRange = (createdAt) => {
  const createdDate = toDateString(createdAt)
  if (!createdDate) return false
  if (startDate.value && createdDate < startDate.value) return false
  if (endDate.value && createdDate > endDate.value) return false
  return true
}

const normalizeMode = (mode) => (mode === 'static_scan' ? 'baseline' : mode)

const resetFilters = () => {
  searchKeyword.value = ''
  selectedMode.value = 'all'
  selectedIssueType.value = 'all'
  startDate.value = ''
  endDate.value = ''
  issueCountRange.value = [0, maxIssueCount.value]
}

const filteredHistoryList = computed(() => {
  const keyword = searchKeyword.value.toLowerCase()
  const [minCount, maxCount] = issueCountRange.value

  return historyList.value.filter(item => {
    const url = String(item.url || '').toLowerCase()
    const modeMatch = selectedMode.value === 'all' || normalizeMode(item.mode) === selectedMode.value
    const keywordMatch = !keyword || url.includes(keyword)
    const timeMatch = inDateRange(item.created_at)
    const issueCount = Number(item.issue_count || 0)
    const issueCountMatch = issueCount >= minCount && issueCount <= maxCount
    const types = getItemIssueTypes(item)
    const typeMatch = selectedIssueType.value === 'all' || types.includes(selectedIssueType.value)
    return modeMatch && keywordMatch && timeMatch && issueCountMatch && typeMatch
  })
})

const allVisibleSelected = computed(() => {
  if (!filteredHistoryList.value.length) return false
  return filteredHistoryList.value.every(item => selectedIds.value.includes(item.id))
})

const toggleSelect = (id) => {
  if (selectedIds.value.includes(id)) {
    selectedIds.value = selectedIds.value.filter(itemId => itemId !== id)
  } else {
    selectedIds.value = [...selectedIds.value, id]
  }
}

const toggleSelectAllVisible = (event) => {
  const checked = event.target.checked
  if (!checked) {
    selectedIds.value = selectedIds.value.filter(
      id => !filteredHistoryList.value.some(item => item.id === id)
    )
    return
  }
  const visibleIds = filteredHistoryList.value.map(item => item.id)
  const merged = new Set([...selectedIds.value, ...visibleIds])
  selectedIds.value = Array.from(merged)
}

const deleteSelected = async () => {
  if (!selectedIds.value.length || deleting.value) return
  const ok = window.confirm(`确认删除选中的 ${selectedIds.value.length} 条历史记录吗？`)
  if (!ok) return

  deleting.value = true
  try {
    const res = await axios.post('http://localhost:8000/api/history/delete', {
      user_id: userStore.userInfo.id,
      ids: selectedIds.value
    })
    if (res.data.status === 'success') {
      historyList.value = historyList.value.filter(item => !selectedIds.value.includes(item.id))
      selectedIds.value = []
      issueCountRange.value = [0, maxIssueCount.value]
    }
  } catch (error) {
    console.error('删除历史记录失败', error)
    window.alert('删除失败，请稍后重试')
  } finally {
    deleting.value = false
  }
}

const formatUrl = (url) => {
  if (!url) return '未知页面'
  const cleanUrl = url.replace(/^https?:\/\//, '')
  return cleanUrl.length > 25 ? cleanUrl.substring(0, 25) + '...' : cleanUrl
}

const viewReport = (item) => {
  try {
    const reportData = typeof item.report_data === 'string' ? JSON.parse(item.report_data) : item.report_data

    // 从历史数据中恢复 checkMode
    if (reportData.mode) {
      auditStore.setCheckMode(reportData.mode)
    } else if (item.mode) {
      auditStore.setCheckMode(item.mode)
    } else {
      // 兜底：如果没有 mode 字段，默认为 baseline
      auditStore.setCheckMode('baseline')
    }

    auditStore.setReportData(reportData)
    router.push('/report')
  } catch (e) {
    console.error("View Report Error: ", e)
    alert('报告数据解析失败，可能已损坏: ' + e.message)
  }
}

const goTo = (path) => router.push(path)
</script>

<style scoped>
.history-page { background: #fbfcfd; min-height: 100vh; padding-top: 60px; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif; }

.container { max-width: 1080px; margin: 0 auto; padding: 0 24px 60px; }
.page-header { margin-bottom: 30px; }
.page-title { font-size: 1.8rem; font-weight: 700; color: #1a1d2e; margin-bottom: 8px; }
.page-desc { color: #6b7280; font-size: 0.95rem; }

.filters-wrap { background: #fff; border: 1px solid #e8eaf0; border-radius: 12px; padding: 14px; margin-bottom: 20px; }
.filters-row { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 10px; align-items: flex-end; }
.top-row .search-item { flex: 1.4; min-width: 320px; }
.filter-item { min-width: 180px; flex: 1; }
.filter-item label { display: block; font-size: 12px; color: #6b7280; margin-bottom: 6px; font-weight: 600; }
.search-input, .filter-select, .date-input { width: 100%; box-sizing: border-box; padding: 9px 12px; border: 1px solid #dbe0ea; border-radius: 8px; font-size: 14px; background: #fff; color: #374151; }
.search-input:focus, .filter-select:focus, .date-input:focus { outline: none; border-color: #8aa7ff; box-shadow: 0 0 0 3px rgba(59,110,248,0.12); }
.date-range-item { flex: 1.2; min-width: 320px; }
.date-range-group { display: flex; align-items: center; gap: 8px; }
.date-sep { color: #6b7280; font-size: 12px; font-weight: 600; }
.result-tip { margin-left: auto; margin-right: 4px; color: #4b5563; font-size: 13px; }
.slider-row { align-items: center; justify-content: space-between; margin-bottom: 4px; }
.slider-label { color: #4b5563; font-size: 13px; font-weight: 600; min-width: 260px; }
.slider-group { display: flex; gap: 8px; flex: 1; }
.slider-group input[type="range"] { width: 100%; }
.actions-row { display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-top: 4px; }
.check-all { display: inline-flex; align-items: center; gap: 8px; color: #4b5563; font-size: 13px; }

.project-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 24px; }
.project-card { position: relative; background: white; border: 1px solid #e8eaf0; border-radius: 12px; overflow: hidden; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; }
.project-card:hover { transform: translateY(-4px); box-shadow: 0 10px 24px rgba(60,72,120,0.08); border-color: rgba(59,110,248,0.3); }
.card-check { position: absolute; top: 10px; left: 10px; z-index: 2; background: rgba(255,255,255,0.8); border-radius: 6px; padding: 2px 4px; }

.project-thumb { height: 150px; position: relative; display: flex; align-items: center; justify-content: center; }
.score-display { font-size: 3rem; font-weight: 900; color: #3b6ef8; text-shadow: 0 4px 12px rgba(59,110,248,0.15); }
.mode-badge { position: absolute; top: 12px; right: 12px; background: rgba(0,0,0,0.4); color: white; font-size: 0.7rem; padding: 3px 8px; border-radius: 4px; font-weight: 600; }

.project-info { padding: 18px; }
.project-name { font-size: 1rem; font-weight: 600; color: #1a1d2e; margin-bottom: 8px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.project-time { font-size: 0.8rem; color: #9ca3af; margin-bottom: 12px; }
.project-meta { font-size: 0.85rem; color: #6b7280; padding-top: 12px; border-top: 1px solid #f0f1f5; }
.project-tags { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 6px; }
.type-tag { background: #eef2ff; color: #3b5bcc; border-radius: 999px; padding: 3px 8px; font-size: 11px; font-weight: 600; }

.state-container { text-align: center; padding: 80px 0; color: #9ca3af; }
.empty-state { background: white; border-radius: 12px; border: 1px dashed #e5e7eb; }
.btn { border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: 600; font-family: inherit; }
.btn-primary { background: #3b6ef8; color: white; }
.btn-primary:hover { background: #256af4; }
.btn-light { background: #f3f4f6; color: #374151; border: 1px solid #e5e7eb; }
.btn-light:hover { background: #e5e7eb; }
.btn-danger { background: #ef4444; color: #fff; }
.btn-danger:hover { background: #dc2626; }
.btn-danger:disabled { background: #fca5a5; cursor: not-allowed; }

.spinner { width: 30px; height: 30px; border: 3px solid #e5e7eb; border-top-color: #3b6ef8; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>