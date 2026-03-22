<template>
  <div class="history-page">
    <AppNavbar variant="full" active-key="history" />

    <div class="container" style="margin-top: 40px;">
      <div v-if="loading" class="state-container">
        <div class="spinner"></div>
        <p style="margin-top:12px;">正在加载真实历史数据...</p>
      </div>
      
      <div v-else-if="historyList.length === 0" class="state-container empty-state">
        <div class="empty-illus" aria-hidden="true"><IconStroke name="inbox" size="lg" /></div>
        <p>暂无走查记录</p>
        <button class="btn btn-primary" style="margin-top: 15px;" @click="goTo('/')">去发起第一次走查</button>
      </div>

      <template v-else>
        <div class="history-content-panel">
        <div class="page-header">
          <h2 class="page-title"><IconStroke name="clock" size="lg" class="page-title-icon" /> 历史走查记录</h2>
          <p class="page-desc">查看和管理过往的 UI 审计报告与走查分析结果</p>
        </div>
        <div class="filters-wrap">
          <div class="filters-block">
            <div class="filter-item">
              <label>走查模式</label>
              <FilterSelect v-model="selectedMode" :options="modeFilterOptions" menu-label="走查模式" />
            </div>
            <div class="filter-item">
              <label>问题类型</label>
              <FilterSelect v-model="selectedIssueType" :options="issueTypeFilterOptions" menu-label="问题类型" />
            </div>
            <div class="filter-item">
              <label>关键词搜索</label>
              <input
                v-model.trim="searchKeyword"
                class="search-input"
                placeholder="请输入网址关键词进行模糊搜索"
                @keyup.enter="applyFilters"
              />
            </div>
            <div class="filter-item filter-item-date">
              <label>走查日期</label>
              <div class="date-range-group">
                <input type="date" v-model="startDate" class="date-input" />
                <span class="date-sep">至</span>
                <input type="date" v-model="endDate" class="date-input" />
              </div>
            </div>
            <div class="filter-actions-span">
              <button type="button" class="btn btn-primary" @click="applyFilters">查询</button>
              <button type="button" class="btn btn-light" @click="resetFilters">重置</button>
            </div>
          </div>
        </div>

        <div v-if="filteredHistoryList.length === 0" class="state-container empty-state">
          <div class="empty-illus empty-illus-muted" aria-hidden="true"><IconStroke name="search" size="lg" /></div>
          <p>未找到匹配的历史记录，请调整筛选条件</p>
        </div>

        <div v-else class="project-grid">
          <div class="project-card" v-for="item in filteredHistoryList" :key="item.id">
            <div class="project-card-main" @click="viewReport(item)">
            <div class="project-thumb" style="background: linear-gradient(135deg, #e8ecf5, #d4daea)">
               <div class="score-display">{{ item.score || 0 }}<span style="font-size:1.2rem;">%</span></div>
               <span class="mode-badge">{{ modeLabel(item.mode) }}</span>
            </div>
            <div class="project-info">
              <div class="project-name" :title="item.url">{{ formatUrl(item.url) }}</div>
              <div class="project-time"><IconStroke name="clock" size="sm" class="project-time-icon" /> {{ item.created_at || '未知时间' }}</div>
              <div class="project-meta">发现问题: <strong style="color:#ef4444">{{ item.issue_count || 0 }}</strong> 项</div>
              <div class="project-tags">
                <span v-for="type in getItemIssueTypes(item)" :key="type" class="type-tag">{{ issueTypeLabel(type) }}</span>
              </div>
            </div>
            </div>
            <button
              type="button"
              class="card-delete-btn"
              :disabled="deletingId === item.id"
              title="删除"
              aria-label="删除此条记录"
              @click.stop="confirmDeleteOne(item)"
            >
              🗑
            </button>
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
import IconStroke from '../components/IconStroke.vue'
import FilterSelect from '../components/FilterSelect.vue'
import { useUserStore } from '../store/user'
import { useAuditStore } from '../store/audit'
import { showConfirm } from '../utils/modal'
import axios from 'axios'

const router = useRouter()
const userStore = useUserStore()
const auditStore = useAuditStore()

const historyList = ref([])
const loading = ref(true)
const deletingId = ref(null)

const searchKeyword = ref('')
const selectedMode = ref('all')
const startDate = ref('')
const endDate = ref('')
const selectedIssueType = ref('all')
const appliedFilters = ref({
  keyword: '',
  mode: 'all',
  issueType: 'all',
  startDate: '',
  endDate: ''
})

const issueTypeMapping = {
  visual: ['视觉', '排版规范', '按钮规范', '表单规范', '导航规范', '展示规范', '间距规范', '像素级对比'],
  interaction: ['交互', '布局', '无障碍'],
  content: ['质量', '性能与质量', '文案', '话术']
}

const modeFilterOptions = [
  { value: 'all', label: '全部模式' },
  { value: 'baseline', label: '基准值模式' },
  { value: 'design', label: '设计稿模式' },
  { value: 'component', label: '组件模式' }
]

const issueTypeFilterOptions = [
  { value: 'all', label: '全部问题类型' },
  { value: 'visual', label: '视觉一致性' },
  { value: 'interaction', label: '交互体验' },
  { value: 'content', label: '文案与话术' }
]

onMounted(async () => {
  if (!userStore.userInfo) {
    router.push('/login')
    return
  }

  try {
    const res = await axios.get(`http://localhost:8000/api/history/${userStore.userInfo.id}`)
    if (res.data.status === 'success') {
      historyList.value = res.data.data
      applyFilters()
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
    baseline: '基准值模式',
    design: '设计稿模式',
    component: '组件模式',
    static_scan: '基准值模式'
  }
  return map[mode] || '其他模式'
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

const normalizeMode = (mode) => (mode === 'static_scan' ? 'baseline' : mode)

const applyFilters = () => {
  appliedFilters.value = {
    keyword: searchKeyword.value.trim().toLowerCase(),
    mode: selectedMode.value,
    issueType: selectedIssueType.value,
    startDate: startDate.value,
    endDate: endDate.value
  }
}

const resetFilters = () => {
  searchKeyword.value = ''
  selectedMode.value = 'all'
  selectedIssueType.value = 'all'
  startDate.value = ''
  endDate.value = ''
  applyFilters()
}

const filteredHistoryList = computed(() => {
  const { keyword, mode, issueType, startDate: fromDate, endDate: toDate } = appliedFilters.value

  return historyList.value.filter(item => {
    const url = String(item.url || '').toLowerCase()
    const modeMatch = mode === 'all' || normalizeMode(item.mode) === mode
    const keywordMatch = !keyword || url.includes(keyword)
    const createdDate = toDateString(item.created_at)
    const timeMatch =
      !!createdDate &&
      (!fromDate || createdDate >= fromDate) &&
      (!toDate || createdDate <= toDate)
    const types = getItemIssueTypes(item)
    const typeMatch = issueType === 'all' || types.includes(issueType)
    return modeMatch && keywordMatch && timeMatch && typeMatch
  })
})

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

const confirmDeleteOne = async (item) => {
  const ok = await showConfirm('确认删除', '确认删除此条记录？')
  if (!ok) return
  deletingId.value = item.id
  try {
    const res = await axios.post('http://localhost:8000/api/history/delete/batch', {
      user_id: userStore.userInfo.id,
      ids: [item.id]
    })
    if (res.data.status === 'success') {
      historyList.value = historyList.value.filter((i) => i.id !== item.id)
      applyFilters()
    }
  } catch (error) {
    console.error('删除历史记录失败', error)
    window.alert('删除失败，请稍后重试')
  } finally {
    deletingId.value = null
  }
}

const goTo = (path) => router.push(path)
</script>

<style scoped>
.history-page { background: #fbfcfd; min-height: 100vh; padding-top: 60px; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif; }

.container { max-width: 1080px; margin: 0 auto; padding: 0 24px 60px; }
.history-content-panel {
  background: #fff;
  border: 1px solid #e8eaf0;
  border-radius: 14px;
  padding: 24px 24px 32px;
  box-sizing: border-box;
  min-height: calc(100vh - 60px - 40px);
}
.page-header { margin-bottom: 30px; }
.page-title { font-size: 1.8rem; font-weight: 700; color: #1a1d2e; margin-bottom: 8px; display: flex; align-items: center; gap: 10px; }
.page-title-icon { color: currentColor; flex-shrink: 0; }
.empty-illus { margin-bottom: 10px; color: #9ca3af; display: flex; justify-content: center; }
.empty-illus-muted { opacity: 0.65; }
.page-desc { color: #6b7280; font-size: 0.95rem; }

.filters-wrap { background: #fff; border: 1px solid #e8eaf0; border-radius: 12px; padding: 14px; margin-bottom: 20px; }
/* 第一行：走查模式 / 问题类型 / 关键词；第二行：走查日期（与上列同宽）+ 查询重置 */
.filters-block {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  align-items: end;
}
.filter-actions-span {
  grid-column: 2 / 4;
  justify-self: end;
  display: flex;
  gap: 8px;
  align-items: center;
}
.filter-item-date {
  grid-column: 1 / 2;
}
@media (max-width: 720px) {
  .filters-block {
    grid-template-columns: minmax(0, 1fr);
  }
  .filter-actions-span {
    grid-column: 1 / -1;
    justify-self: stretch;
    justify-content: flex-end;
  }
  .filter-item-date {
    grid-column: 1 / -1;
  }
}
.filter-item { min-width: 0; }
.filter-item label { display: block; font-size: 12px; color: #6b7280; margin-bottom: 6px; font-weight: 600; }
.search-input, .date-input {
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
  padding: 9px 12px;
  border: 1px solid #dbe0ea;
  border-radius: 8px;
  font-size: 14px;
  background: #fff;
  color: #374151;
}
.search-input:focus, .date-input:focus { outline: none; border-color: #8aa7ff; box-shadow: 0 0 0 3px rgba(26, 106, 255,0.12); }
.date-range-group { display: flex; align-items: center; gap: 6px; min-width: 0; }
.date-range-group .date-input { flex: 1; min-width: 0; }
.date-sep { color: #6b7280; font-size: 12px; font-weight: 600; flex-shrink: 0; }
.project-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 24px; }
.project-card { position: relative; background: white; border: 1px solid #e8eaf0; border-radius: 12px; overflow: hidden; transition: transform 0.2s, box-shadow 0.2s; }
.project-card:hover { transform: translateY(-4px); box-shadow: 0 10px 24px rgba(60,72,120,0.08); border-color: rgba(26, 106, 255,0.3); }
.project-card-main { cursor: pointer; }
/* 与规范管理 .btn-del 一致：无背景无边框，灰→悬停红 */
.card-delete-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 4;
  margin: 0;
  padding: 0;
  background: none;
  border: none;
  font-size: 1.05rem;
  line-height: 1;
  color: #9ca3af;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.15s, color 0.15s;
}
.project-card:hover .card-delete-btn { opacity: 1; }
.card-delete-btn:hover:not(:disabled) {
  color: #ef4444;
}
.card-delete-btn:focus-visible {
  outline: 2px solid rgba(26, 106, 255, 0.35);
  outline-offset: 2px;
}
.card-delete-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.project-time-icon { color: #9ca3af; margin-right: 4px; vertical-align: middle; }

.project-thumb { height: 150px; position: relative; display: flex; align-items: center; justify-content: center; }
.score-display { font-size: 3rem; font-weight: 900; color: #1A6AFF; text-shadow: 0 4px 12px rgba(26, 106, 255,0.15); }
.mode-badge { position: absolute; top: 12px; left: 12px; background: rgba(0,0,0,0.4); color: white; font-size: 0.7rem; padding: 3px 8px; border-radius: 4px; font-weight: 600; }

.project-info { padding: 18px; }
.project-name { font-size: 1rem; font-weight: 600; color: #1a1d2e; margin-bottom: 8px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.project-time { font-size: 0.8rem; color: #9ca3af; margin-bottom: 12px; }
.project-meta { font-size: 0.85rem; color: #6b7280; padding-top: 12px; border-top: 1px solid #f0f1f5; }
.project-tags { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 6px; }
.type-tag { background: #eef2ff; color: #1A6AFF; border-radius: 999px; padding: 3px 8px; font-size: 11px; font-weight: 600; }

.state-container { text-align: center; padding: 80px 0; color: #9ca3af; }
.empty-state { background: white; border-radius: 12px; border: 1px dashed #e5e7eb; }
.btn { border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: 600; font-family: inherit; }
.btn-primary { background: #1A6AFF; color: white; }
.btn-primary:hover { background: #1557e6; }
.btn-light { background: #f3f4f6; color: #374151; border: 1px solid #e5e7eb; }
.btn-light:hover { background: #e5e7eb; }

.spinner { width: 30px; height: 30px; border: 3px solid #e5e7eb; border-top-color: #1A6AFF; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>