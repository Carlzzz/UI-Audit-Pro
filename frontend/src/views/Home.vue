<template>
  <div class="home-wrapper">
    <AppNavbar variant="full" active-key="scan" />

    <section class="hero-section">
      <div class="container">
        <h1 class="hero-title">提升 UI 走查效率</h1>
        <p class="hero-subtitle">一键自动化审计网页 UI 规范、前端还原度与设计一致性。</p>

        <div class="entry-card">
          <div class="url-input-wrap">
            <div class="input-group">
              <span class="input-icon">🔗</span>
              <input type="url" class="input-field" v-model="url" placeholder="输入待检查的网页地址 (https://...)">
            </div>
          </div>

          <div class="mode-selector">
            <div class="mode-option" :class="{ selected: mode === 'baseline' }" @click="mode = 'baseline'">
              <div class="mode-option-icon">⇌</div>
              <div class="mode-text">
                <div class="mode-option-title">基准值自动化走查</div>
                <div class="mode-option-desc">自动审计 UI 规范数值、色值、间距等一致性</div>
              </div>
            </div>
            <div class="mode-option" :class="{ selected: mode === 'component' }" @click="mode = 'component'">
              <div class="mode-option-icon">品</div>
              <div class="mode-text">
                <div class="mode-option-title">组件模式走查</div>
                <div class="mode-option-desc">细化至各类组件的尺寸、状态及间距检测</div>
              </div>
            </div>
            <div class="mode-option" :class="{ selected: mode === 'design' }" @click="mode = 'design'">
              <div class="mode-option-icon">🖼</div>
              <div class="mode-text">
                <div class="mode-option-title">设计稿对比走查</div>
                <div class="mode-option-desc">Figma 插件或图片上传，AI 像素级差异分析</div>
              </div>
            </div>
          </div>

          <button class="btn btn-primary btn-lg start-btn" @click="startConfig">
            <span>⚡</span> 开始配置走查
          </button>

          <div class="feature-tags">
            <div class="feature-tag"><span>✓</span> 支持桌面端走查</div>
            <div class="feature-tag"><span>✓</span> 支持移动端适配检测</div>
            <div class="feature-tag"><span>✓</span> AI 视觉差值分析</div>
          </div>
        </div>
      </div>
    </section>

    <section class="recent-section">
      <div class="container">
        <div class="section-header">
          <div class="section-title">
            <span style="color:var(--primary); font-size:1.2rem;">⏱</span> 最近的走查项目
          </div>
          <a class="view-all-link" href="#" @click.prevent="goTo('/history')">查看全部</a>
        </div>
        
        <div v-if="loadingHistory" style="text-align:center; padding: 40px; color:#9ca3af; width: 100%;">
          数据加载中...
        </div>
        
        <div v-else-if="recentHistory.length === 0" style="text-align:center; padding: 40px; color:#9ca3af; border: 1px dashed #e8eaf0; border-radius: 12px; background: white;">
          暂无历史走查记录，快去发起第一次走查吧！
        </div>

        <div class="project-grid" v-else>
          <div class="project-card" v-for="item in recentHistory" :key="item.id" @click="viewReport(item)">
            <div class="project-thumb" style="background: linear-gradient(135deg, #e8ecf5, #d4daea);">
              <div class="score-display">
                {{ item.score || 0 }}<span style="font-size:1.2rem;">%</span>
              </div>
              <span class="status-badge" :class="item.mode === 'baseline' ? 'status-completed' : 'status-reviewing'">
                {{ item.mode === 'baseline' ? '规范基准' : '设计稿' }}
              </span>
            </div>
            <div class="project-info">
              <div class="project-name" :title="item.url">{{ formatUrl(item.url) }}</div>
              <div class="project-time">🕐 {{ item.created_at || '未知时间' }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <footer class="footer">
      © 2026 DesignCheck Pro - 自动化设计走查专家
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppNavbar from '../components/AppNavbar.vue'
import { useAuditStore } from '../store/audit'
import { useUserStore } from '../store/user'
import { showMsg } from '../utils/modal'
import axios from 'axios'

const router = useRouter()
const auditStore = useAuditStore()
const userStore = useUserStore()

const url = ref('')
const mode = ref('baseline')

// 历史记录状态
const recentHistory = ref([])
const loadingHistory = ref(true)

// 页面挂载时拉取真实数据
onMounted(async () => {
  if (userStore.userInfo) {
    try {
      const res = await axios.get(`http://localhost:8000/api/history/${userStore.userInfo.id}`)
      if (res.data.status === 'success') {
        // 取出最新的 4 条记录
        recentHistory.value = res.data.data.slice(0, 4)
      }
    } catch (error) {
      console.error('获取最近记录失败', error)
    } finally {
      loadingHistory.value = false
    }
  } else {
    loadingHistory.value = false
  }
})

// 格式化 URL
const formatUrl = (urlStr) => {
  if (!urlStr) return '未知页面'
  const cleanUrl = urlStr.replace(/^https?:\/\//, '')
  return cleanUrl.length > 25 ? cleanUrl.substring(0, 25) + '...' : cleanUrl
}

// 点击历史卡片查看详情
const viewReport = (item) => {
  try {
    const reportData = JSON.parse(item.report_data)
    auditStore.setReportData(reportData)
    router.push('/report')
  } catch (e) {
    showMsg('错误', '报告数据解析失败，可能已损坏', 'error')
  }
}

const startConfig = () => {
  if (!url.value) return showMsg('提示', '请输入目标网页地址', 'warning')
  auditStore.setTargetUrl(url.value)
  auditStore.setCheckMode(mode.value)
  // 必须跳转到 audit-setup
  router.push('/audit-setup')
}

const goTo = (path) => router.push(path)
</script>

<style scoped>
.home-wrapper { min-height: 100vh; background: #fbfcfd; display: flex; flex-direction: column; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif; }

.hero-section { padding-top: 100px; padding-bottom: 50px; text-align: center; }
.hero-title { font-size: 2.8rem; font-weight: 700; color: #1a1d2e; margin-bottom: 16px; letter-spacing: -0.02em; }
.hero-subtitle { font-size: 1.05rem; color: #6b7280; margin-bottom: 40px; }
.entry-card { background: #fff; border-radius: 16px; border: 1px solid #e8eaf0; box-shadow: 0 10px 40px rgba(60,72,120,0.06); padding: 32px; max-width: 900px; margin: 0 auto; }
.url-input-wrap { margin-bottom: 24px; }
.input-group { position: relative; }
.input-icon { position: absolute; left: 16px; top: 50%; transform: translateY(-50%); color: #9ca3af; font-size: 1.1rem; }
.input-field { width: 100%; font-size: 1.05rem; padding: 16px 16px 16px 48px; border: 1px solid #e2e4ec; border-radius: 10px; outline: none; transition: border-color 0.2s; box-sizing: border-box;}
.input-field:focus { border-color: #3b6ef8; box-shadow: 0 0 0 3px rgba(59,110,248,0.1); }
.mode-selector { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
.mode-option { display: flex; align-items: flex-start; gap: 12px; padding: 18px; border: 1.5px solid #e2e4ec; border-radius: 12px; cursor: pointer; transition: all 0.2s; background: #fff; text-align: left;}
.mode-option:hover { border-color: #3b6ef8; background: #f0f4ff; }
.mode-option.selected { border-color: #3b6ef8; background: #f0f4ff; box-shadow: 0 4px 12px rgba(59,110,248,0.08); }
.mode-option-icon { font-size: 24px; color: #3b6ef8; flex-shrink: 0; }
.mode-option-title { font-size: 0.95rem; font-weight: 600; color: #3b6ef8; margin-bottom: 4px; }
.mode-option-desc { font-size: 0.8rem; color: #6b7280; line-height: 1.4; }
.start-btn { width: 100%; padding: 16px; font-size: 1.1rem; border-radius: 10px; display: flex; justify-content: center; gap: 8px; border: none; background: #3b6ef8; color: white; cursor: pointer; font-weight: 600;}
.start-btn:hover { background: #256af4; }
.feature-tags { display: flex; align-items: center; justify-content: center; gap: 24px; margin-top: 20px; }
.feature-tag { display: flex; align-items: center; gap: 6px; font-size: 0.82rem; color: #9ca3af; }
.feature-tag span { color: #10b981; font-weight: bold; }
.recent-section { padding-bottom: 60px; flex: 1; }
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; max-width: 1080px; margin: 0 auto 20px;}
.section-title { font-size: 1.1rem; font-weight: 700; color: #1a1d2e; display: flex; align-items: center; gap: 8px; }
.view-all-link { font-size: 0.88rem; color: #3b6ef8; cursor: pointer; text-decoration: none;}

/* 历史卡片样式 */
.project-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; max-width: 1080px; margin: 0 auto; }
.project-card { background: #fff; border-radius: 12px; border: 1px solid #e8eaf0; overflow: hidden; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; }
.project-card:hover { transform: translateY(-4px); box-shadow: 0 10px 24px rgba(60,72,120,0.08); border-color: rgba(59,110,248,0.3); }
.project-thumb { height: 140px; position: relative; display: flex; align-items: center; justify-content: center; overflow: hidden; }
.score-display { font-size: 2.5rem; font-weight: 900; color: #3b6ef8; text-shadow: 0 4px 12px rgba(59,110,248,0.15); }
.status-badge { position: absolute; top: 12px; right: 12px; font-size: 0.65rem; font-weight: 800; padding: 3px 8px; border-radius: 4px; letter-spacing: 0.05em; }
.status-completed { background: #10b981; color: #fff; } 
.status-reviewing { background: #3b6ef8; color: #fff; }

.project-info { padding: 16px; }
.project-name { font-size: 0.95rem; font-weight: 600; color: #1a1d2e; margin-bottom: 6px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;}
.project-time { font-size: 0.8rem; color: #9ca3af; }
.footer { text-align: center; padding: 24px; font-size: 0.85rem; color: #9ca3af; border-top: 1px solid #e8eaf0; background: #fff; }
</style>