<template>
  <div class="home-wrapper">
    <AppNavbar variant="full" active-key="scan" />

    <div class="home-main-with-bg">
    <section class="hero-section">
      <div class="container">
        <h1 class="hero-title">提升 UI 走查效率</h1>
        <p class="hero-subtitle">一键自动化审计网页 UI 规范、前端还原度与设计一致性。</p>

        <div class="entry-card">
          <div class="url-input-wrap">
            <div class="input-group">
              <span class="input-icon" aria-hidden="true"><IconStroke name="link" size="md" /></span>
              <input type="url" class="input-field" v-model="url" placeholder="输入待检查的网页地址 (https://...)">
            </div>
          </div>

          <div class="mode-selector">
            <div class="mode-option" :class="{ selected: mode === 'baseline' }" @click="mode = 'baseline'">
              <div class="mode-option-icon" aria-hidden="true"><IconStroke name="baseline" size="lg" /></div>
              <div class="mode-text">
                <div class="mode-option-title">基准值模式</div>
                <div class="mode-option-desc">自动审计 UI 规范数值、色值、间距等一致性</div>
              </div>
            </div>
            <div class="mode-option" :class="{ selected: mode === 'component' }" @click="mode = 'component'">
              <div class="mode-option-icon" aria-hidden="true"><IconStroke name="component" size="lg" /></div>
              <div class="mode-text">
                <div class="mode-option-title">组件模式</div>
                <div class="mode-option-desc">细化至各类组件的尺寸、状态及间距检测</div>
              </div>
            </div>
            <div class="mode-option" :class="{ selected: mode === 'design' }" @click="mode = 'design'">
              <div class="mode-option-icon" aria-hidden="true"><IconStroke name="design" size="lg" /></div>
              <div class="mode-text">
                <div class="mode-option-title">设计稿模式</div>
                <div class="mode-option-desc">Figma 插件或图片上传，AI 像素级差异分析</div>
              </div>
            </div>
          </div>

          <button class="btn btn-primary btn-lg start-btn" @click="startConfig">
            <IconStroke name="bolt" size="md" /> 开始配置走查
          </button>

          <div class="feature-tags">
            <div class="feature-tag"><IconStroke name="check" size="sm" class="feature-check" /> 支持桌面端走查</div>
            <div class="feature-tag"><IconStroke name="check" size="sm" class="feature-check" /> 支持移动端适配检测</div>
            <div class="feature-tag"><IconStroke name="check" size="sm" class="feature-check" /> AI 视觉差值分析</div>
          </div>
        </div>
      </div>
    </section>

    <section class="recent-section">
      <div class="recent-section-inner">
      <div class="container">
        <div class="section-header">
          <div class="section-title">
            <IconStroke name="clock" size="md" class="section-title-icon" /> 最近的走查项目
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
            <div class="project-thumb">
              <div class="thumb-glow"></div>
              <div class="score-display">
                {{ item.score || 0 }}<span style="font-size:20px;">%</span>
              </div>
              <span class="status-badge">{{ modeBadgeLabel(item.mode) }}</span>
            </div>
            <div class="project-info">
              <div class="project-name" :title="item.url">{{ formatUrl(item.url) }}</div>
              <div class="project-time"><IconStroke name="clock" size="sm" class="inline-time-icon" /> {{ item.created_at || '未知时间' }}</div>
            </div>
          </div>
        </div>
      </div>
      </div>
    </section>

    <footer class="footer">
      © 2026 DesignCheck Pro - 自动化设计走查专家
    </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppNavbar from '../components/AppNavbar.vue'
import IconStroke from '../components/IconStroke.vue'
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
    const reportData = typeof item.report_data === 'string' ? JSON.parse(item.report_data) : item.report_data
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
  auditStore.clearSessionDraft()
  // 必须跳转到 audit-setup
  router.push('/audit-setup')
}

const goTo = (path) => router.push(path)

const modeBadgeLabel = (mode) => {
  const m = mode === 'static_scan' ? 'baseline' : mode
  const map = {
    baseline: '基准值模式',
    design: '设计稿模式',
    component: '组件模式'
  }
  return map[m] || '基准值模式'
}
</script>

<style scoped>
.home-wrapper { min-height: 100vh; background: #fbfcfd; display: flex; flex-direction: column; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif; overflow-x: hidden; position: relative; z-index: 0; }

.home-main-with-bg {
  --hero-bottom-gap: 48px;
  flex: 1;
  position: relative;
  padding-top: 100px;
  padding-bottom: var(--hero-bottom-gap);
  background-image: url('/images/home-section-bg.png');
  background-color: #fbfcfd;
  background-size: cover;
  background-position: top center;
  background-repeat: no-repeat;
}
.home-main-with-bg::after {
  content: '';
  position: absolute;
  left: 0; right: 0; bottom: 0;
  height: 80px;
  background: linear-gradient(to bottom, transparent, #fbfcfd);
  pointer-events: none;
}

.hero-section {
  text-align: center;
}
.hero-title { font-size: 44px; font-weight: 700; color: #1a1d2e; margin-bottom: 16px; letter-spacing: -0.02em; }
.hero-subtitle { font-size: 16px; color: #6b7280; margin-bottom: 40px; }
.entry-card { background: #fff; border-radius: 16px; border: 1px solid #e8eaf0; box-shadow: 0 10px 40px rgba(60,72,120,0.06); padding: 32px; max-width: 1080px; width: 100%; margin: 0 auto; box-sizing: border-box; }
.url-input-wrap { margin-bottom: 24px; }
.input-group { position: relative; }
.input-icon { position: absolute; left: 16px; top: 50%; transform: translateY(-50%); color: #9ca3af; display: flex; align-items: center; justify-content: center; }
.input-field { width: 100%; height: 52px; font-size: 16px; padding: 0 16px 0 48px; border: 1px solid #e2e4ec; border-radius: 12px; outline: none; transition: border-color 0.2s; box-sizing: border-box;}
.input-field:focus { border-color: #1A6AFF; box-shadow: 0 0 0 3px rgba(26, 106, 255,0.1); }
.mode-selector { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
.mode-option { display: flex; align-items: flex-start; gap: 12px; padding: 16px; border: 1.5px solid #e2e4ec; border-radius: 12px; cursor: pointer; transition: all 0.2s; background: #fff; text-align: left;}
.mode-option:hover { border-color: #1A6AFF; background: #f0f4ff; }
.mode-option.selected { border-color: #1A6AFF; background: #f0f4ff; box-shadow: 0 4px 12px rgba(26, 106, 255,0.08); }
.mode-option { color: #1A6AFF; }
.mode-option-icon { display: flex; align-items: center; justify-content: center; color: currentColor; flex-shrink: 0; }
.section-title-icon { color: currentColor; margin-right: 4px; }
.feature-check { color: currentColor !important; }
.inline-time-icon { color: #9ca3af; margin-right: 4px; }
.mode-option-title { font-size: 14px; font-weight: 600; color: #1A6AFF; margin-bottom: 4px; }
.mode-option-desc { font-size: 12px; color: #6b7280; line-height: 1.4; }
.start-btn { width: 100%; height: 52px; padding: 0; font-size: 18px; border-radius: 12px; display: flex; align-items: center; justify-content: center; gap: 8px; border: none; background: #1A6AFF; color: white; cursor: pointer; font-weight: 600;}
.start-btn:hover { background: #1557e6; }
.feature-tags { display: flex; align-items: center; justify-content: center; gap: 24px; margin-top: 20px; }
.feature-tag { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #9ca3af; }
.feature-tag span { color: #10b981; font-weight: bold; }
.recent-section { margin-top: 48px; flex: 1; padding: 0 24px; }
.recent-section-inner { max-width: 1052px; width: 100%; margin: 0 auto; padding: 32px 24px 60px; background: #fff; border-radius: 16px; box-sizing: border-box; }
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; max-width: 1080px; margin: 0 auto 20px;}
.section-title { font-size: 18px; font-weight: 700; color: #1a1d2e; display: flex; align-items: center; gap: 8px; }
.view-all-link { font-size: 14px; color: #1A6AFF; cursor: pointer; text-decoration: none;}

/* 历史卡片样式 */
.project-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; max-width: 1080px; margin: 0 auto; }
.project-card {
  background: #fff;
  border-radius: 16px;
  border: 1px solid rgba(226, 230, 240, 0.6);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
  box-shadow: 0 2px 12px rgba(60, 72, 120, 0.04);
}
.project-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 40px rgba(26, 106, 255, 0.10), 0 4px 12px rgba(60, 72, 120, 0.06);
  border-color: rgba(26, 106, 255, 0.2);
}
.project-thumb {
  height: 148px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: linear-gradient(160deg, #eef2fb 0%, #e4e9f7 40%, #dde4f5 70%, #e8e4f3 100%);
}
.thumb-glow {
  position: absolute;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(100, 100, 255, 0.30) 0%, rgba(130, 120, 255, 0.18) 40%, transparent 70%);
  filter: blur(20px);
  pointer-events: none;
  transition: transform 0.4s ease, opacity 0.3s ease;
}
.project-card:hover .thumb-glow {
  transform: scale(1.25);
  opacity: 0.85;
}
.score-display {
  position: relative;
  z-index: 1;
  font-size: 42px;
  font-weight: 900;
  color: #1A6AFF;
  letter-spacing: -0.02em;
}
.status-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 2;
  font-size: 10px;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 6px;
  letter-spacing: 0.04em;
  background: linear-gradient(135deg, #1A6AFF, #5b8cf7);
  color: #fff;
  box-shadow: 0 2px 8px rgba(26, 106, 255, 0.25);
}

.project-info { padding: 16px; border-top: 1px solid rgba(226, 230, 240, 0.5); }
.project-name { font-size: 14px; font-weight: 600; color: #1a1d2e; margin-bottom: 8px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.project-time { font-size: 12px; color: #9ca3af; display: flex; align-items: center; gap: 4px; }
.footer { text-align: center; padding: 24px; font-size: 14px; color: #6b7280; background: transparent; border: none; border-top: none; box-shadow: none; }
</style>