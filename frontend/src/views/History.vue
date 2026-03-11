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

      <div class="project-grid" v-else>
        <div class="project-card" v-for="item in historyList" :key="item.id" @click="viewReport(item)">
          <div class="project-thumb" style="background: linear-gradient(135deg, #e8ecf5, #d4daea)">
             <div class="score-display">{{ item.score || 0 }}<span style="font-size:1.2rem;">%</span></div>
             <span class="mode-badge">{{ item.mode === 'baseline' ? '规范基准' : '设计稿对比' }}</span>
          </div>
          <div class="project-info">
            <div class="project-name" :title="item.url">{{ formatUrl(item.url) }}</div>
            <div class="project-time">🕐 {{ item.created_at || '未知时间' }}</div>
            <div class="project-meta">发现问题: <strong style="color:#ef4444">{{ item.issue_count || 0 }}</strong> 项</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
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

onMounted(async () => {
  if (!userStore.userInfo) {
    router.push('/login')
    return
  }

  try {
    const res = await axios.get(`http://localhost:8000/api/history/${userStore.userInfo.id}`)
    if (res.data.status === 'success') {
      historyList.value = res.data.data
    }
  } catch (error) {
    console.error("加载历史记录失败", error)
  } finally {
    loading.value = false
  }
})

const formatUrl = (url) => {
  if (!url) return '未知页面'
  const cleanUrl = url.replace(/^https?:\/\//, '')
  return cleanUrl.length > 25 ? cleanUrl.substring(0, 25) + '...' : cleanUrl
}

const viewReport = (item) => {
  try {
    const reportData = JSON.parse(item.report_data)
    auditStore.setReportData(reportData)
    router.push('/report')
  } catch (e) {
    alert('报告数据解析失败，可能已损坏')
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

.project-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 24px; }
.project-card { background: white; border: 1px solid #e8eaf0; border-radius: 12px; overflow: hidden; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; }
.project-card:hover { transform: translateY(-4px); box-shadow: 0 10px 24px rgba(60,72,120,0.08); border-color: rgba(59,110,248,0.3); }

.project-thumb { height: 150px; position: relative; display: flex; align-items: center; justify-content: center; }
.score-display { font-size: 3rem; font-weight: 900; color: #3b6ef8; text-shadow: 0 4px 12px rgba(59,110,248,0.15); }
.mode-badge { position: absolute; top: 12px; right: 12px; background: rgba(0,0,0,0.4); color: white; font-size: 0.7rem; padding: 3px 8px; border-radius: 4px; font-weight: 600; }

.project-info { padding: 18px; }
.project-name { font-size: 1rem; font-weight: 600; color: #1a1d2e; margin-bottom: 8px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.project-time { font-size: 0.8rem; color: #9ca3af; margin-bottom: 12px; }
.project-meta { font-size: 0.85rem; color: #6b7280; padding-top: 12px; border-top: 1px solid #f0f1f5; }

.state-container { text-align: center; padding: 80px 0; color: #9ca3af; }
.empty-state { background: white; border-radius: 12px; border: 1px dashed #e5e7eb; }
.btn { border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: 600; font-family: inherit; }
.btn-primary { background: #3b6ef8; color: white; }
.btn-primary:hover { background: #256af4; }

.spinner { width: 30px; height: 30px; border: 3px solid #e5e7eb; border-top-color: #3b6ef8; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>