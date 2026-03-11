<template>
  <div class="dashboard-layout" v-if="reportData">
    <AppNavbar variant="breadcrumb">
      <template #actions>
        <button class="btn btn-primary" style="margin-right:24px;" @click="goTo('/report')">📄 生成详细报告</button>
      </template>
    </AppNavbar>

    <div class="dashboard-main">
      <div class="canvas-area">
        <div class="canvas-header">
          <div class="canvas-header-title">👁 页面实时预览 (将鼠标悬停在框选区域查看详情)</div>
          <div class="canvas-legend">
            <span><span class="legend-dot" style="background:#ef4444;"></span>严重不符</span>
            <span><span class="legend-dot" style="background:#f59e0b;"></span>视觉偏离</span>
          </div>
        </div>
        
        <div class="canvas-viewport">
          <div class="mock-device" :style="{ transform: `scale(${zoom / 100})` }">
            <img v-if="reportData.screenshot" :src="'data:image/png;base64,' + reportData.screenshot" class="actual-img" />
            <div v-else class="actual-img-placeholder">📸 后端未返回截图</div>
            
            <template v-if="reportData.issues && reportData.issues.length > 0">
              <div v-for="issue in reportData.issues" :key="issue.id"
                   v-show="issue.rect"
                   class="annotation-box"
                   :class="issue.level === 'high' ? 'ann-critical' : 'ann-warning'"
                   :style="{ 
                     top: issue.rect.top + 'px', 
                     left: issue.rect.left + 'px', 
                     width: issue.rect.width + 'px', 
                     height: issue.rect.height + 'px' 
                   }">
                
                <span class="annotation-label">{{ issue.category }}异常</span>
                
                <div class="annotation-popover">
                  <div class="popover-title">{{ issue.title }}</div>
                  <div class="popover-desc"><span class="pop-lbl">实测：</span>{{ issue.desc }}</div>
                  <div class="popover-sugg"><span class="pop-lbl">建议：</span>{{ issue.suggestion }}</div>
                </div>

              </div>
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
          <div class="sidebar-header-hint">检测到 <strong style="color:#ef4444;">{{ reportData.issueCount || 0 }}</strong> 个不符合规范的属性</div>
        </div>
        
        <div class="sidebar-body">
          <table class="audit-table">
            <thead>
              <tr><th style="width:25%">审计项</th><th style="width:25%">实测值</th><th style="width:35%">标准值/建议</th><th style="width:15%; text-align:right;">状态</th></tr>
            </thead>
            <tbody>
              <tr><td colspan="4" class="group-title">1. 异常诊断列表</td></tr>
              
              <template v-if="reportData.issues && reportData.issues.length > 0">
                <tr v-for="issue in reportData.issues" :key="issue.id" class="data-row">
                  <td class="attr-name" :title="issue.title">{{ (issue.title || '未知').substring(0,8) }}</td>
                  <td class="actual-val" :class="issue.level==='high' ? 'val-err' : 'val-warn'">{{ extractValue(issue.desc, true) }}</td>
                  <td class="standard-val">
                    <div style="font-size:0.8rem; line-height:1.4; font-weight:600;">{{ extractValue(issue.desc, false) }}</div>
                    <div class="fix-link" :title="issue.suggestion">建议：{{ (issue.suggestion || '请参考规范').substring(0,8) }}...</div>
                  </td>
                  <td style="text-align:right;"><span class="status-tag" :class="issue.level==='high'?'st-fail':'st-warn'">{{ issue.level==='high'?'不符合':'偏离' }}</span></td>
                </tr>
              </template>
              <tr v-else><td colspan="4" style="text-align:center; padding: 30px; color:#9ca3af;">无样式异常数据</td></tr>
            </tbody>
          </table>
          
          <div class="sidebar-footer">
            <div class="fix-suggestion-box">
              <div class="fs-title"><span>🤖</span> AI 整体诊断结论</div>
              <div class="fs-text">{{ reportData.diagnosis || '大模型未返回整体诊断。' }}</div>
            </div>
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
import { useAuditStore } from '../store/audit'

const router = useRouter()
const auditStore = useAuditStore()
const reportData = auditStore.reportData

const zoom = ref(50)

onMounted(() => {
  if (!reportData) setTimeout(() => router.push('/'), 1500)
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
.btn { border: none; cursor: pointer; font-family: inherit; font-weight: 600; transition: background 0.2s; }
.btn-primary { background: #3b6ef8; color: white; border-radius: 6px; padding: 8px 16px; font-size: 0.85rem; }
.btn-primary:hover { background: #256af4; }

.dashboard-main { flex: 1; display: flex; overflow: hidden; padding: 24px; gap: 24px; }

.canvas-area { flex: 1; display: flex; flex-direction: column; background: white; border-radius: 12px; border: 1px solid #e5e7eb; overflow: hidden; position: relative;}
.canvas-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; border-bottom: 1px solid #e5e7eb; background: white; z-index: 10;}
.canvas-header-title { font-weight: 700; color: #1a1d2e; font-size: 1.05rem; }
.canvas-legend { display: flex; gap: 16px; font-size: 0.85rem; color: #4b5563; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 6px; }
.canvas-viewport { 
  flex: 1; 
  background: #eef1f6; 
  overflow: auto; 
  display: flex; 
  justify-content: center; 
  align-items: flex-start; /* 🚨 必须是 flex-start，防止容器拉伸变形 */
  padding: 40px; 
  position: relative; 
}

.mock-device { 
  background: white; 
  box-shadow: 0 20px 40px rgba(0,0,0,0.15); 
  position: relative; 
  transform-origin: top center; 
  transition: transform 0.15s ease; 
  display: inline-block; /* 🚨 核心：让 div 紧紧包裹住原比例图片 */
  line-height: 0; /* 消除幽灵底边距 */
}

.actual-img { 
  display: block; 
  max-width: none; /* 🚨 绝对核心：禁止图片被 CSS 缩放，保持 1:1 原生像素！ */
}
.actual-img-placeholder { padding: 80px 20px; text-align: center; color: #9ca3af; height: 100%; display:flex; flex-direction:column; justify-content:center; align-items:center;}

.zoom-controls { position: absolute; bottom: 20px; right: 20px; background: white; border: 1px solid #e5e7eb; border-radius: 8px; display: flex; align-items: center; padding: 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
.zoom-controls button { background: none; border: none; padding: 4px 12px; font-size: 1.2rem; cursor: pointer; color: #4b5563; }
.zoom-controls span { font-size: 0.85rem; font-weight: 600; width: 45px; text-align: center; }

/* 🌟 核心标注框 (加入防膨胀与指针变动) */
.annotation-box { 
  position: absolute; 
  border: 2px solid; 
  box-sizing: border-box; /* 🚨 彻底解决边框导致的尺寸膨胀偏移 */
  cursor: crosshair; 
  box-shadow: 0 0 0 3px rgba(255,255,255,0.7); 
  z-index: 5;
  transition: background 0.2s, z-index 0.2s;
}
.annotation-box:hover { 
  z-index: 20; 
  background: rgba(255,255,255,0.25); 
}
.annotation-label { position: absolute; top: -24px; left: -2px; padding: 4px 8px; font-size: 13px; font-weight: 600; color: white; border-radius: 4px 4px 4px 0; white-space: nowrap; }
.ann-critical { border-color: #ef4444; } .ann-critical .annotation-label { background: #ef4444; }
.ann-warning { border-color: #f59e0b; } .ann-warning .annotation-label { background: #f59e0b; }

/* 🌟 悬停高级气泡 (Tooltip Popover) */
.annotation-popover {
  position: absolute;
  bottom: calc(100% + 14px);
  left: 50%;
  transform: translateX(-50%) translateY(10px);
  background: #1a1d2e;
  padding: 14px 16px;
  border-radius: 8px;
  width: max-content;
  max-width: 280px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  pointer-events: none; /* 防止遮挡鼠标导致闪烁 */
}
.annotation-box:hover .annotation-popover {
  opacity: 1;
  visibility: visible;
  transform: translateX(-50%) translateY(0);
}
.annotation-popover::after {
  content: ''; position: absolute; top: 100%; left: 50%; transform: translateX(-50%);
  border-width: 6px; border-style: solid; border-color: #1a1d2e transparent transparent transparent;
}
.popover-title { font-size: 0.95rem; font-weight: 700; color: white; margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 6px;}
.popover-desc, .popover-sugg { font-size: 0.82rem; color: white; margin-bottom: 6px; line-height: 1.5; white-space: normal;}
.pop-lbl { color: #9ca3af; font-weight: 600;}

/* 右侧表格 */
.sidebar { width: 480px; background: white; border-radius: 12px; border: 1px solid #e5e7eb; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);}
.sidebar-header { padding: 24px; border-bottom: 1px solid #e5e7eb; }
.sidebar-header-title { font-size: 1.2rem; font-weight: 700; color: #1a1d2e; margin-bottom: 8px; }
.sidebar-header-hint { font-size: 0.85rem; color: #6b7280;}
.sidebar-body { flex: 1; overflow-y: auto; display: flex; flex-direction: column; }

.audit-table { width: 100%; border-collapse: collapse; table-layout: fixed;}
.audit-table th { padding: 14px 24px; font-size: 0.85rem; font-weight: 500; color: #9ca3af; text-align: left; border-bottom: 1px solid #e5e7eb; background: #f9fafb; }
.group-title { padding: 20px 24px 10px; font-size: 0.95rem; font-weight: 600; color: #1a1d2e; }
.data-row { border-bottom: 1px solid #f3f4f6; }
.data-row td { padding: 16px 24px; font-size: 0.9rem; vertical-align: top;}
.attr-name { color: #4b5563; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
.val-err { color: #ef4444; font-weight: 600; } .val-warn { color: #f59e0b; font-weight: 600; } .val-ok { color: #10b981; font-weight: 600; }
.standard-val { color: #1a1d2e; font-weight: 500;}
.fix-link { color: #3b6ef8; font-size: 0.8rem; margin-top: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}

.status-tag { padding: 4px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: 500; display: inline-block;}
.st-fail { color: #ef4444; background: #fee2e2; border: 1px solid #fca5a5;}
.st-warn { color: #f59e0b; background: #fef3c7; border: 1px solid #fcd34d;}

.sidebar-footer { padding: 24px; margin-top: auto; border-top: 1px solid #e5e7eb;}
.fix-suggestion-box { background: #f0f4ff; border-radius: 8px; padding: 20px; }
.fs-title { font-size: 0.9rem; font-weight: 600; color: #3b6ef8; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }
.fs-title span { font-size: 16px; }
.fs-text { font-size: 0.85rem; color: #4b5563; line-height: 1.6; }
</style>