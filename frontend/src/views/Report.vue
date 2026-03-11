<template>
  <div v-if="reportData" class="rpt-body">
    <AppNavbar variant="report" class="no-print">
      <template #actions>
        <button class="btn btn-ghost" @click="goTo('/dashboard')">🔍 查看可视化看板</button>
        <button class="btn btn-primary" @click="exportPDF">⬇ 导出报告</button>
      </template>
    </AppNavbar>

    <div class="rpt-page">
      <div class="rpt-inner">
        <div class="rpt-breadcrumb no-print">
          <a href="#" @click.prevent="goTo('/')">🏠 首页</a> <span class="sep">›</span>
          <span>自动化走查</span> <span class="sep">›</span> <span class="cur">报告详情</span>
        </div>

        <div class="rpt-layout">
          <div id="left-col">
            <div class="rpt-card score-card">
              <div class="score-card-hdg">设计还原度评分（{{ auditStore.checkMode === 'baseline' ? '基准值模式' : '设计稿模式' }}）</div>
              <div class="score-body">
                <div class="ring-wrap">
                  <svg class="ring-svg" width="110" height="110" viewBox="0 0 110 110">
                    <circle class="ring-bg" cx="55" cy="55" r="44" />
                    <circle class="ring-fg" cx="55" cy="55" r="44" :stroke-dashoffset="276.5 - (276.5 * (reportData.score || 0) / 100)" stroke-dasharray="276.5" />
                  </svg>
                  <div class="ring-label">
                    <span class="ring-pct">{{ reportData.score || 0 }}%</span>
                    <span class="ring-sub">还原度</span>
                  </div>
                </div>
                <div class="score-detail">
                  <div class="score-badge">↑ 击败了全国 92% 的项目</div>
                  <div class="score-desc">本次走查发现 {{ reportData.issueCount || 0 }} 个规范问题。建议优先修复高优问题。</div>
                  <div class="score-stats" v-if="auditStore.checkMode === 'baseline'">
                    <div class="stat-block">
                      <div class="stat-val">{{ reportData.compliance || 0 }}%</div>
                      <div class="stat-label">规范符合度</div>
                    </div>
                    <div class="stat-block stat-issues">
                      <div class="stat-issue-val">{{ reportData.issueCount || 0 }} 个问题点</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <div class="issue-list-hd">
                <div class="issue-list-title">关键问题清单 <span class="issue-list-cnt">{{ filteredIssues.length }}</span></div>
                <div class="issue-filter-btns no-print">
                  <button class="filter-btn" :class="{active: filter === 'all'}" @click="filter = 'all'">全部</button>
                  <button class="filter-btn" :class="{active: filter === 'high'}" @click="filter = 'high'">高严重度</button>
                </div>
              </div>
              
              <div class="issue-card" v-for="issue in filteredIssues" :key="issue.id">
                <div class="issue-card-row">
                  
                  <div class="issue-thumb" @click="goTo('/dashboard')">
                    <div class="thumb-labels">
                      <span class="thumb-tag" v-if="auditStore.checkMode === 'design'">设计稿</span>
                      <span class="thumb-tag">前端实际</span>
                    </div>
                    
                    <div class="real-thumb-crop" v-if="reportData.screenshot && issue.rect"
                         :style="getThumbStyle(issue.rect)">
                       <div class="real-thumb-box" :style="getThumbBoxStyle(issue.rect)"></div>
                    </div>
                    <div class="issue-thumb-inner" v-else>
                       <div class="tb tb-light"></div><div class="tb tb-red"></div><div class="tb tb-light"></div>
                    </div>
                    
                    <div class="issue-thumb-footer no-print">点击查看对比详情</div>
                  </div>

                  <div class="issue-body">
                    <div class="issue-badge-row">
                      <span class="issue-badge" :class="issue.level === 'high' ? 'badge-critical' : 'badge-warning'">
                        {{ issue.level === 'high' ? 'CRITICAL 严重' : 'WARNING 中等' }}
                      </span>
                      <span class="issue-assignee">分类：{{ issue.category }}</span>
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
              
              <div v-if="filteredIssues.length === 0" style="text-align:center; padding: 40px; color:#9ca3af; background:white; border-radius:12px; border:1px solid #e8eaf0;">
                太棒了！当前分类下暂无问题。
              </div>
            </div>
          </div>

          <div class="rpt-sidebar">
            <div class="meta-card">
              <div class="meta-card-hd">报告元数据</div>
              <div class="meta-row"><span class="meta-lbl">目标页面</span><span class="meta-val"><a :href="formattedUrl" target="_blank">点击访问</a></span></div>
              <div class="meta-row"><span class="meta-lbl">操作员</span><span class="meta-val">{{ userStore.userInfo ? userStore.userInfo.username : 'Agent' }}</span></div>
              <div class="meta-row"><span class="meta-lbl">基准模式</span><span class="meta-val">{{ auditStore.checkMode === 'baseline' ? '规范基准' : 'UI 设计稿' }}</span></div>
            </div>

            <div class="help-card no-print">
              <div class="help-title">需要帮助？</div>
              <div class="help-desc">如果走查结果存在误报，您可以手动标记该条目为“已忽略”。</div>
              <div class="help-btn-wrap">
                <button class="help-btn">反馈问题</button>
                <div class="help-tooltip">此功能开发中，敬请期待</div>
              </div>
            </div>

            <div class="meta-card" style="padding:15px; margin-top:15px;">
              <div style="font-weight:bold; font-size:0.84rem; margin-bottom:10px;">实际页面快照</div>
              <img v-if="reportData.screenshot" :src="'data:image/png;base64,' + reportData.screenshot" style="width:100%; border:1px solid #e8eaf0; border-radius:8px;"/>
              <div v-else style="padding:40px 10px; text-align:center; background:#f9fafb; color:#9ca3af; font-size:0.8rem; border-radius:8px; border:1px dashed #e8eaf0;">
                此条走查记录暂无快照数据
              </div>
            </div>
            
            <div class="trend-card no-print" style="margin-top:15px;">
              <div class="trend-title">近期历史还原度趋势</div>
              <div class="trend-chart" v-if="trendData.length > 0">
                <div class="bar-wrap" v-for="(item, idx) in trendData" :key="idx">
                  <div class="bar-val" :style="{ color: idx === trendData.length - 1 ? '#3b6ef8' : '#9ca3af' }">{{ item.score }}%</div>
                  <div class="bar-fill" :class="{ today: idx === trendData.length - 1 }" :style="`height:${Math.max(item.score * 0.6, 10)}px;`"></div>
                  <div class="bar-date">{{ item.date }}</div>
                </div>
              </div>
              <div v-else style="font-size:0.8rem; color:#9ca3af; text-align:center; padding: 15px 0;">暂无足够历史数据</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else style="padding: 100px; text-align: center;">加载中...</div>
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

const filter = ref('all')
const trendData = ref([])

const filteredIssues = computed(() => {
  if (!reportData || !reportData.issues) return []
  return filter.value === 'all' ? reportData.issues : reportData.issues.filter(i => i.level === filter.value)
})

const formattedUrl = computed(() => {
  if (!reportData || !reportData.url) return '#'
  let url = reportData.url
  if (!/^https?:\/\//i.test(url)) url = 'http://' + url
  return url
})

const getThumbStyle = (rect) => {
  const x = Math.max(0, rect.left - 30)
  const y = Math.max(0, rect.top - 30)
  return {
    backgroundImage: `url(data:image/png;base64,${reportData.screenshot})`,
    backgroundPosition: `-${x}px -${y}px`
  }
}

const getThumbBoxStyle = (rect) => {
  const xOffset = rect.left < 30 ? rect.left : 30
  const yOffset = rect.top < 30 ? rect.top : 30
  return {
    top: `${yOffset}px`,
    left: `${xOffset}px`,
    width: `${rect.width}px`,
    height: `${rect.height}px`
  }
}

onMounted(async () => {
  if (!reportData) {
    router.push('/')
    return
  }
  if (userStore.userInfo) {
    try {
      const res = await axios.get(`http://localhost:8000/api/history/${userStore.userInfo.id}`)
      if (res.data.status === 'success') {
        const history = res.data.data
        if (history && history.length > 0) {
          const recent4 = history.slice(0, 4).reverse()
          trendData.value = recent4.map(h => ({
            score: h.score || 0,
            date: h.created_at ? h.created_at.substring(5, 10) : '未知'
          }))
        }
      }
    } catch (e) {
      console.error('获取趋势图数据失败', e)
    }
  }
})

const exportPDF = () => window.print()
const goTo = (path) => router.push(path)
</script>

<style scoped>
.rpt-body { background: #f4f6fb; min-height: 100vh; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif; }
.rpt-page { padding-top: 80px; padding-bottom: 60px; }
.rpt-inner { max-width: 1080px; margin: 0 auto; padding: 0 24px; }
.rpt-breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.85rem; color: #9ca3af; margin-bottom: 22px; }
.rpt-breadcrumb a { color: #6b7280; text-decoration: none; transition: color 0.2s;} .rpt-breadcrumb a:hover{ color: #3b6ef8;} .rpt-breadcrumb .cur { color: #1a1d2e; font-weight: 500; }
.rpt-layout { display: grid; grid-template-columns: 1fr 300px; gap: 20px; align-items: flex-start; }

.btn { border: none; font-family: inherit; cursor: pointer; transition: all 0.2s; font-weight:600;}
.btn-primary { background: #3b6ef8; color: white; border-radius: 6px; padding: 8px 16px; font-size:0.85rem;}
.btn-primary:hover { background: #256af4; }
.btn-ghost { background: transparent; color: #6b7280; border: 1px solid #e8eaf0; border-radius: 6px; padding: 8px 16px; font-size: 0.85rem; }
.btn-ghost:hover { background: #f9fafb; color: #1a1d2e; }
.rpt-card { background: #fff; border: 1px solid #e8eaf0; border-radius: 14px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(60, 72, 120, .04); overflow: hidden; }

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
.score-badge { display: inline-flex; background: #d1fae5; color: #065f46; padding: 4px 12px; border-radius: 99px; font-size: 0.78rem; font-weight: 600; margin-bottom: 12px; }
.score-desc { font-size: 0.86rem; color: #6b7280; line-height: 1.75; margin-bottom: 18px; }
.score-stats { display: flex; gap: 28px; align-items: flex-start; }
.stat-val { font-size: 1.2rem; font-weight: 800; color: #1a1d2e; }
.stat-label { font-size: 0.75rem; color: #9ca3af; margin-top: 4px; }

.issue-list-hd { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; } 
.issue-list-title { font-weight: 700; font-size: 1rem; color: #1a1d2e; }
.issue-list-cnt { background: #f3f4f6; color: #6b7280; font-size: 0.78rem; font-weight: 600; padding: 2px 8px; border-radius: 99px; margin-left: 6px; }
.issue-filter-btns { display: flex; gap: 8px; }
.filter-btn { padding: 5px 14px; border-radius: 99px; border: 1px solid #e8eaf0; font-size: 0.78rem; background: #fff; color: #6b7280; cursor: pointer; transition: all .15s; font-weight: 500;}
.filter-btn.active { background: #3b6ef8; color: #fff; border-color: #3b6ef8; }

.issue-card { background: #fff; border: 1px solid #e8eaf0; border-radius: 12px; overflow: hidden; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(60,72,120,.05); transition: transform 0.2s, box-shadow 0.2s; }
.issue-card:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(60,72,120,.08); }
.issue-card-row { display: flex; }

.issue-thumb { width: 180px; background: #f3f4f6; position: relative; display: flex; align-items: center; justify-content: center; cursor: pointer; overflow: hidden;}
.thumb-labels { position: absolute; top: 8px; left: 8px; right: 8px; display: flex; justify-content: space-between; z-index: 10; pointer-events: none;} 
.thumb-tag { font-size: 0.65rem; background: rgba(0,0,0,.6); color: #fff; padding: 3px 8px; border-radius: 4px; font-weight:600;}
.real-thumb-crop { width: 100%; height: 100%; position: absolute; inset: 0; background-repeat: no-repeat; z-index: 1; }
.real-thumb-box { position: absolute; border: 2px solid #ef4444; background: rgba(239, 68, 68, 0.2); box-shadow: 0 0 0 2000px rgba(0,0,0,0.5); border-radius: 2px; }

.issue-thumb-inner { width: 78%; display: flex; gap: 6px; z-index: 5; } .tb { height: 30px; border-radius: 5px; } .tb-light { background: rgba(255,255,255,.55); flex: 1; } .tb-red { border: 2px solid rgba(239,68,68,.8); background: rgba(239,68,68,.08); flex: 1.5; }
.issue-thumb-footer { position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,.5); color: #fff; font-size: 0.7rem; text-align: center; padding: 6px 0; z-index: 10; }

.issue-body { flex: 1; padding: 16px 20px; display: flex; flex-direction: column; gap: 8px; }
.issue-badge { display: inline-flex; align-items: center; gap: 4px; font-size: 0.7rem; font-weight: 800; padding: 3px 10px; border-radius: 4px; letter-spacing: .04em; color: white; } 
.badge-critical { background: #ef4444; } .badge-warning { background: #f59e0b; }
.issue-assignee { font-size: 0.78rem; color: #9ca3af; margin-left: auto; font-weight:500;}
.issue-title { font-weight: 700; font-size: 1rem; color: #1a1d2e;} .issue-desc { font-size: 0.85rem; color: #6b7280; line-height: 1.6; }
.issue-fix { background: #f8faff; border-left: 3px solid #3b6ef8; padding: 10px 14px; margin-top: 4px; border-radius:0 6px 6px 0;} 
.issue-fix-label { font-size: 0.75rem; color: #3b6ef8; font-weight: 700; margin-bottom:4px;} 
.issue-fix-text { font-size: 0.8rem; font-family: monospace; color: #4b5563; }

.rpt-sidebar { display: flex; flex-direction: column; }
.meta-card { background: #fff; border: 1px solid #e8eaf0; border-radius: 14px; box-shadow: 0 1px 4px rgba(60,72,120,.06); overflow: hidden; } 
.meta-card-hd { padding: 14px 20px; font-weight: 700; font-size: 0.9rem; background: #fafbff; border-bottom: 1px solid #f0f1f6; color:#1a1d2e;}
.meta-row { display: flex; justify-content: space-between; padding: 12px 20px; border-bottom: 1px solid #f4f5f9; font-size: 0.85rem; } .meta-row:last-child { border-bottom: none; }
.meta-lbl { color: #9ca3af; } .meta-val { font-weight: 600; text-align: right; color:#4b5563;} .meta-val a { color: #3b6ef8; text-decoration: none; }

.help-card { background: #3b6ef8; border-radius: 14px; padding: 20px; color: #fff; margin-top: 16px; } 
.help-title { font-weight: 700; font-size: 0.95rem; margin-bottom: 8px; } 
.help-desc { font-size: 0.8rem; opacity: .9; margin-bottom: 16px; line-height: 1.5; } 
.help-btn-wrap { position: relative; display: inline-block; width: 100%; }
.help-btn { width: 100%; padding: 10px; border-radius: 8px; background: rgba(255,255,255,.2); border: 1px solid rgba(255,255,255,.3); color: #fff; cursor: pointer; font-size: 0.85rem; font-weight: 600; transition: background 0.2s;}
.help-btn:hover { background: rgba(255,255,255,.3); }
.help-tooltip { position: absolute; bottom: 100%; left: 50%; transform: translateX(-50%); background: #1a1d2e; color: white; padding: 8px 12px; border-radius: 6px; font-size: 0.75rem; opacity: 0; visibility: hidden; transition: all 0.2s ease; white-space: nowrap; margin-bottom: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); pointer-events: none; z-index: 10; font-weight:500;}
.help-tooltip::after { content: ''; position: absolute; top: 100%; left: 50%; transform: translateX(-50%); border-width: 5px; border-style: solid; border-color: #1a1d2e transparent transparent transparent; }
.help-btn-wrap:hover .help-tooltip { opacity: 1; visibility: visible; margin-bottom: 12px; }

.trend-card { background: #fff; border: 1px solid #e8eaf0; border-radius: 14px; padding: 20px; box-shadow: 0 1px 4px rgba(60, 72, 120, .06); }
.trend-title { font-size: 0.9rem; font-weight: 700; color: #1a1d2e; margin-bottom: 18px; }
.trend-chart { display: flex; align-items: flex-end; gap: 10px; height: 80px; }
.bar-wrap { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px; justify-content: flex-end; }
.bar-fill { width: 100%; border-radius: 4px 4px 0 0; background: #dbeafe; transition: height 0.5s ease; min-height: 4px; }
.bar-fill.today { background: #3b6ef8; }
.bar-val { font-size: 0.7rem; font-weight: 800; order: -1; }
.bar-date { font-size: 0.65rem; color: #9ca3af; font-weight:500;}

@media print {
  .no-print { display: none !important; }
  .rpt-body { background: white !important; }
  .rpt-page { padding-top: 0 !important; }
  .rpt-card { box-shadow: none !important; border: 1px solid #ddd !important; }
}
</style>