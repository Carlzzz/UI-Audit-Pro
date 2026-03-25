<template>
    <div class="scan-wrapper">
      <AppNavbar variant="scan" :show-user-dropdown="false">
        <template #actions>
          <button class="btn-icon" @click="cancelScan" title="取消走查">✕</button>
        </template>
      </AppNavbar>
  
      <div class="scan-page">
        <div class="scan-main-stack">
        <div class="scan-preview">
          <div class="preview-topbar"></div>
          <div class="preview-highlight"></div>
          <div class="preview-row">
            <div class="preview-cell"></div><div class="preview-cell"></div><div class="preview-cell"></div>
          </div>
          <div class="preview-line"></div>
          <div class="preview-line w80"></div>
          <div class="preview-line w60"></div>
          <div class="preview-line w40"></div>
        </div>
  
        <h2 class="scan-main-title">正在进行全链路设计走查...</h2>
        <p class="scan-main-desc">AI 正在深度分析您的设计稿，识别潜在的视觉差异、组件规范及交互逻辑问题。</p>
  
        <div class="scan-task-id">当前任务 ID <strong>{{ taskId }}</strong></div>
        <div class="progress-card">
          <div class="progress-header">
            <span class="progress-label">
              <IconStroke name="chart-trend" size="sm" strokeWeight="2" class="progress-chart-icon" />
              总扫描进度
            </span>
            <span class="progress-pct">{{ progress }}%</span>
          </div>
          <div class="progress-eta">预计剩余时间：约 {{ eta }} 秒</div>
          <div class="progress-bar-wrap">
            <div class="progress-bar-fill" :style="{ width: progress + '%' }"></div>
          </div>
  
          <div class="checklist-title">检查清单</div>
          <div class="checklist">
            <div class="check-item" :class="getStepClass(0)">
              <span class="check-item-left"><span class="check-icon" v-html="getStepIcon(0)"></span>视觉比对走查</span>
              <span class="check-status" :class="getStatusClass(0)">{{ getStatusText(0) }}</span>
            </div>
            <div class="check-item" :class="getStepClass(1)">
              <span class="check-item-left"><span class="check-icon" v-html="getStepIcon(1)"></span>组件规范一致性校验</span>
              <span class="check-status" :class="getStatusClass(1)">{{ getStatusText(1) }}</span>
            </div>
            <div class="check-item" :class="getStepClass(2)">
              <span class="check-item-left"><span class="check-icon" v-html="getStepIcon(2)"></span>全局样式审计（色值、字阶）</span>
              <span class="check-status" :class="getStatusClass(2)">{{ getStatusText(2) }}</span>
            </div>
            <div class="check-item" :class="getStepClass(3)">
              <span class="check-item-left"><span class="check-icon" v-html="getStepIcon(3)"></span>AI 诊断报告生成</span>
              <span class="check-status" :class="getStatusClass(3)">{{ getStatusText(3) }}</span>
            </div>
          </div>
        </div>
        </div>

        <footer class="scan-footer-copyright">
          版权所有 © 中国移动云能力中心. 保留所有权利
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
  import axios from 'axios'
  import { useUserStore } from '../store/user'
  
  const router = useRouter()
  const auditStore = useAuditStore()
  
  const taskId = ref('TASK-' + Date.now().toString().slice(-6))
  const progress = ref(0)
  const eta = ref(45)
  const currentStep = ref(0) // 0~3
  
  const getStepClass = (step) => {
    if (currentStep.value > step) return 'done'
    if (currentStep.value === step) return 'running'
    return 'pending'
  }
  const getStepIcon = (step) => {
    if (currentStep.value > step) return '✓'
    if (currentStep.value === step) return '<div class="spinner" style="width:14px;height:14px;border:2px solid var(--primary);border-top-color:transparent;border-radius:50%;animation:spin 1s linear infinite;"></div>'
    return '⊙'
  }
  const getStatusClass = (step) => {
    if (currentStep.value > step) return 'status-done'
    if (currentStep.value === step) return 'status-running'
    return 'status-pending'
  }
  const getStatusText = (step) => {
    if (currentStep.value > step) return '已完成'
    if (currentStep.value === step) return '• 进行中'
    return '未开始'
  }
  
  const cancelScan = () => {
    if(confirm('确定取消走查任务吗？')) router.push('/')
  }
  
  onMounted(async () => {
    const timer = setInterval(() => {
      if (progress.value < 90) {
        progress.value += 1
        eta.value = Math.max(0, Math.floor((100 - progress.value) * 0.4))
        currentStep.value = Math.floor(progress.value / 25)
      }
    }, 300)
  
    try {
    const cfg = auditStore.taskConfig
    if (!cfg || typeof cfg !== 'object') {
      clearInterval(timer)
      alert('走查配置缺失，请返回「新建走查」页面完成规则设置后再开启走查。')
      router.push('/audit-setup')
      return
    }
    const res = await axios.post('http://localhost:8000/api/audit', {
      url: auditStore.targetUrl,
      mode: auditStore.checkMode,
      config: JSON.parse(JSON.stringify(cfg)),
      user_id: useUserStore().userInfo.id
    })
  
      clearInterval(timer)
      if (res.data.status === 'success') {
        progress.value = 100
        eta.value = 0
        currentStep.value = 4
        auditStore.setReportData(res.data.data)
        
        // 【修复点】：扫描完成后，优先跳转到 Dashboard 看板页，而不是直接去 Report
        setTimeout(() => router.push('/dashboard'), 800)
      } else {
        alert('分析失败: ' + res.data.message)
        router.push('/')
      }
    } catch(e) {
      clearInterval(timer)
      alert('请求失败，请检查 Python 后端是否启动')
      router.push('/')
    }
  })
  </script>
  
  <style scoped>
  .scan-wrapper { background: var(--bg-page); min-height: 100vh; }
  .scan-page {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    min-height: calc(100vh - 60px);
    box-sizing: border-box;
    /* 整体较原先再下移 50px；底部留白由页脚 margin 控制 */
    padding: calc(50px + clamp(48px, 8vh, 100px)) 24px calc(24px + env(safe-area-inset-bottom, 0px));
  }
  .scan-main-stack {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    max-width: 560px;
  }
  .scan-preview { width: 340px; max-width: 90%; background: white; border-radius: var(--radius-lg); padding: 18px; box-shadow: var(--shadow-lg); margin-bottom: 36px; position: relative; overflow: hidden; }
  .scan-preview::before { content: ''; position: absolute; top: 0; left: -100%; width: 60%; height: 100%; background: linear-gradient(90deg, transparent, rgba(26, 106, 255, 0.08), transparent); animation: scan-sweep 2s linear infinite; }
  @keyframes scan-sweep { 0% { left: -60%; } 100% { left: 100%; } }
  .preview-topbar { height: 10px; background: #e2e8f0; border-radius: 5px; margin-bottom: 12px; width: 70%; }
  .preview-highlight { height: 4px; background: linear-gradient(90deg, var(--primary), var(--secondary)); border-radius: 2px; margin-bottom: 12px; width: 100%; }
  .preview-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 8px; }
  .preview-cell { height: 18px; background: #f0f2f8; border-radius: 4px; }
  .preview-line { height: 8px; background: #f0f2f8; border-radius: 4px; margin-bottom: 6px; }
  .preview-line.w80 { width: 80%; } .preview-line.w60 { width: 60%; } .preview-line.w40 { width: 40%; }
  .scan-main-title { font-size: 1.8rem; font-weight: 700; color: var(--text-primary); margin-bottom: 10px; text-align: center; }
  .scan-main-desc { color: var(--text-secondary); font-size: 0.9rem; text-align: center; max-width: 380px; margin-bottom: 32px; line-height: 1.7; }
  .progress-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 28px;
    width: 100%;
    max-width: 560px;
    box-shadow: var(--shadow-md);
    margin-bottom: 0;
  }
  .scan-task-id {
    align-self: flex-start;
    margin: 0 0 10px 0;
    font-size: 0.72rem;
    color: var(--text-muted);
    background: #f8faff;
    border: 1px solid #e5e7eb;
    border-radius: 999px;
    padding: 3px 10px;
    line-height: 1.2;
  }
  .scan-task-id strong {
    color: #1a1d2e;
    font-weight: 700;
  }
  .progress-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
  .progress-label { font-size: 0.92rem; font-weight: 600; display: flex; align-items: center; gap: 10px; }
  .progress-chart-icon { flex-shrink: 0; color: var(--primary); }
  .progress-pct { font-size: 1.2rem; font-weight: 700; color: var(--primary); }
  .progress-eta { font-size: 0.78rem; color: var(--text-muted); margin-bottom: 12px; }
  .progress-bar-wrap { margin-bottom: 20px; height: 6px; background: #eef2ff; border-radius: 99px; overflow: hidden; }
  .progress-bar-fill { height: 100%; background: linear-gradient(90deg, var(--primary), var(--secondary)); transition: width 0.3s; }
  .checklist-title { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.06em; }
  .checklist { display: flex; flex-direction: column; gap: 8px; }
  .check-item { display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; border-radius: var(--radius-sm); font-size: 0.88rem; }
  .check-item.done { background: #f0fdf4; }
  .check-item.running { background: var(--primary-light); }
  .check-item.pending { opacity: 0.5; }
  .check-icon { font-size: 16px; margin-right: 10px; display: inline-flex; align-items: center; }
  .check-item-left { display: flex; align-items: center; }
  .check-status { font-size: 0.76rem; font-weight: 600; padding: 2px 8px; border-radius: 4px; }
  .status-done { background: #d1fae5; color: #065f46; }
  .status-running { background: transparent; color: var(--primary); border: 1px solid var(--primary); }
  .status-pending { background: #f3f4f6; color: var(--text-muted); }
  .scan-footer-copyright {
    margin: 40px 0 0;
    padding: 0 16px;
    box-sizing: border-box;
    width: 100%;
    max-width: 560px;
    text-align: center;
    font-size: 0.75rem;
    color: var(--text-muted);
    line-height: 1.5;
  }
  @keyframes spin { 100% { transform: rotate(360deg); } }
  </style>