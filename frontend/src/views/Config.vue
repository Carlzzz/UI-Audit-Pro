<template>
  <div class="page-container">
    <AppNavbar variant="full" active-key="config" />

    <div class="spec-page">
      <div class="breadcrumb">
        <span>🏠</span>
        <a href="#" @click.prevent="$router.push('/')">首页</a>
        <span class="sep">›</span>
        <span class="cur">全局规范管理</span>
      </div>

      <div class="spec-header">
        <div>
          <div class="spec-title">全局基准值规范</div>
          <div class="spec-subtitle">定义设计走查的全局基准规范，后续每次走查都会默认代入此模板。</div>
        </div>
        <div class="spec-header-actions">
          <button class="btn btn-ghost" @click="$router.push('/')">取消</button>
          <button class="btn btn-primary" @click="saveConfig">💾 保存配置模板</button>
        </div>
      </div>

      <div class="spec-tabs">
        <div class="spec-tab" :class="{ active: mode === 'baseline' }" @click="mode = 'baseline'">⇌ 基准值模式</div>
        <div class="spec-tab" :class="{ active: mode === 'design' }" @click="mode = 'design'">🖼 设计稿模式</div>
      </div>

      <div v-show="mode === 'baseline'">
        
        <div class="category-section">
          <div class="category-title"><div class="cat-icon" style="background:#eef2ff; color:var(--primary);">✨</div>1. 视觉一致性标准</div>
          
          <div class="two-col-row">
            <div class="spec-card">
              <div class="card-title">◎ 品牌色盘与近色检测</div>
              <div id="color-list" style="margin-top:15px;">
                <div class="color-row" v-for="(color, idx) in config.colors" :key="idx" @click="editColor(idx)">
                  <div class="color-swatch-sq" :style="{ background: color.hex }"></div>
                  <input type="text" class="color-edit-input" v-model="color.label" title="点击修改名称" @click.stop />
                  <input type="text" class="color-edit-input hex-font" v-model="color.hex" title="点击修改色值" @click.stop />
                  <button class="color-del-btn" @click.stop="removeColor(idx)">🗑</button>
                </div>
              </div>
              <div class="add-color-row" @click="addColor"><span>＋</span> 添加色值</div>
              
              <div class="switch-row" style="margin-top:16px; border-top:1px dashed var(--border); padding-top:16px;">
                <div class="switch-info"><div class="switch-name">自动检测并标记“相近但不同”的色彩误差</div></div>
                <div class="toggle" :class="{ on: config.nearColorCheck }" @click="config.nearColorCheck = !config.nearColorCheck"></div>
              </div>
              
              <div class="slider-box" v-show="config.nearColorCheck">
                <div class="slider-header">
                    <span class="slider-title">色差容忍阈值</span>
                    <span class="slider-val">{{ config.colorTolerance }}</span>
                </div>
                <div class="slider-hint">数值越低，要求越严格（建议保持在 10~20）</div>
                <input type="range" min="0" max="50" v-model="config.colorTolerance" class="custom-range">
              </div>
            </div>

            <div class="spec-card">
              <div class="card-title">Tr 字体与排版系统</div>
              <div class="field-row" style="margin-top:10px;">
                <div class="field-label">字体族 (Font Family)</div>
                <input class="field-input" type="text" v-model="config.fontFamily">
              </div>
              <div class="field-row">
                <div class="field-label">行高基数 (Line Heights)</div>
                <input class="field-input" type="text" v-model="config.lineHeights">
              </div>
              <div class="field-row">
                <div class="field-label">允许的字阶 (FONT SIZES)</div>
                <div class="token-row">
                  <span class="token-pill" v-for="(t, idx) in config.fontTokens" :key="idx">{{ t }}px <span class="rm" @click="config.fontTokens.splice(idx,1)">×</span></span>
                  <span class="token-add-btn" @click="addToken('font')">＋ 添加</span>
                </div>
              </div>
            </div>
          </div>

          <div class="two-col-row">
            <div class="spec-card">
              <div class="card-title">⊞ 间距与栅格</div>
              <div class="field-row" style="margin-top:10px;">
                <div class="field-label">间距令牌 (SPACING TOKENS)</div>
                <div class="token-row" style="margin-bottom:20px;">
                  <span class="token-pill" v-for="(t, idx) in config.spacingTokens" :key="idx">{{ t }}px <span class="rm" @click="config.spacingTokens.splice(idx,1)">×</span></span>
                  <span class="token-add-btn" @click="addToken('spacing')">＋ 添加</span>
                </div>
              </div>
              <div class="switch-row" style="border-top:1px dashed var(--border); padding-top:16px;">
                <div class="switch-name">栅格对齐检测 (px)</div>
                <div class="toggle" :class="{ on: config.gridCheck }" @click="config.gridCheck = !config.gridCheck"></div>
              </div>
              <div class="token-row" style="margin-top:12px;" v-show="config.gridCheck">
                <span class="sq-tag" v-for="(g, idx) in config.gridTokens" :key="idx">{{ g }}px <span class="rm" @click="config.gridTokens.splice(idx,1)">🗑</span></span>
                <span class="input-add-btn" @click="addToken('grid')">＋ 增加</span>
              </div>
            </div>

            <div class="spec-card">
              <div class="card-title">◈ 圆角与投影</div>
              <div class="field-row" style="margin-top:10px;">
                <div class="field-label">圆角规范 (BORDER RADIUS)</div>
                <div class="token-row" style="margin-bottom:20px;">
                  <span class="sq-tag" v-for="(r, idx) in config.radiusTokens" :key="idx">{{ r }}px <span class="rm" @click="config.radiusTokens.splice(idx,1)">🗑</span></span>
                  <span class="input-add-btn" @click="addToken('radius')">＋ 增加</span>
                </div>
              </div>
              <div class="switch-row" style="border-top: 1px dashed var(--border); padding-top:16px; margin-bottom:12px;">
                <div class="switch-info"><div class="switch-name">阴影规范检测</div></div>
                <div class="toggle" :class="{ on: config.shadowCheck }" @click="config.shadowCheck = !config.shadowCheck"></div>
              </div>
              <div class="field-row" v-show="config.shadowCheck">
                <div class="field-label">投影预设</div>
                <select class="spec-select" v-model="config.shadowPreset">
                  <option value="ant">符合 Ant Design 投影规范</option>
                  <option value="material">符合 Material Design 投影规范</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <div class="category-section">
          <div class="category-title"><div class="cat-icon" style="background:#f0fdf4; color:var(--success);">👆</div>2. 交互与布局标准</div>
          <div class="three-col-row">
            <div class="spec-card">
              <div class="card-title" style="font-size:0.95rem;">点击区域与状态</div>
              <div class="hotzone-row" style="margin: 20px 0;">
                <div class="hotzone-label">最小点击热区</div>
                <div style="display:flex; align-items:center; gap:6px;"><input class="hotzone-val" type="number" v-model="config.minClickArea"> px</div>
              </div>
              <div class="switch-row" style="border-top:1px dashed var(--border); padding-top:16px;">
                <div class="switch-info"><div class="switch-name">组件触发状态</div><div class="switch-desc">检测 Hover/Active 反馈</div></div>
                <div class="toggle" :class="{ on: config.hoverCheck }" @click="config.hoverCheck = !config.hoverCheck"></div>
              </div>
            </div>
            
            <div class="spec-card">
              <div class="card-title" style="font-size:0.95rem;">文本溢出与响应式</div>
              <div class="field-row" style="margin:16px 0;">
                <select class="spec-select" v-model="config.textOverflow">
                  <option value="ellipsis">默认使用省略号 (Ellipsis)</option>
                  <option value="wrap">换行显示</option>
                </select>
              </div>
              <div class="switch-row" style="border-top:1px dashed var(--border); padding-top:16px;">
                <div class="switch-info"><div class="switch-name">响应式适配检测</div></div>
                <div class="toggle" :class="{ on: config.responsiveCheck }" @click="config.responsiveCheck = !config.responsiveCheck"></div>
              </div>
            </div>

            <div class="spec-card">
              <div class="card-title" style="font-size:0.95rem;">异常状态覆盖</div>
              <div class="switch-row" style="border:none; padding:0; margin-top:16px;">
                <div class="switch-info"><div class="switch-name">空状态覆盖</div></div>
                <div class="toggle" :class="{ on: config.emptyStateCheck }" @click="config.emptyStateCheck = !config.emptyStateCheck"></div>
              </div>
              <div class="switch-row" style="padding-top:16px; margin-top:16px; border-top:1px dashed var(--border);">
                <div class="switch-info"><div class="switch-name">加载状态预设</div></div>
                <div class="toggle" :class="{ on: config.loadingStateCheck }" @click="config.loadingStateCheck = !config.loadingStateCheck"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="category-section">
          <div class="category-title"><div class="cat-icon" style="background:#fff7ed; color:#ea580c;">♿</div>3. 无障碍与合规性 (Accessibility/W3C)</div>
          <div class="four-col-row">
            <div class="spec-card flex-center-card">
              <div class="card-title-sm">色彩对比度阈值</div>
              <div class="big-val">4.5:1</div>
              <div class="badge badge-success">AA级标准</div>
            </div>
            <div class="spec-card flex-between-card">
              <div>
                <div class="card-title-sm" style="margin-bottom:6px;">图片 Alt 属性</div>
                <div class="switch-desc">检测 &lt;img&gt; 替代文本</div>
              </div>
              <div class="toggle" :class="{ on: config.altCheck }" @click="config.altCheck = !config.altCheck"></div>
            </div>
            <div class="spec-card flex-between-card">
              <div>
                <div class="card-title-sm" style="margin-bottom:6px;">DOM 语义化</div>
                <div class="switch-desc">检测 H1~H6 层级顺序</div>
              </div>
              <div class="toggle" :class="{ on: config.domSemantics }" @click="config.domSemantics = !config.domSemantics"></div>
            </div>
            <div class="spec-card flex-between-card">
              <div>
                <div class="card-title-sm" style="margin-bottom:6px;">焦点顺序逻辑</div>
                <div class="switch-desc">检测 Tab 键切换流转</div>
              </div>
              <div class="toggle" :class="{ on: config.focusOrder }" @click="config.focusOrder = !config.focusOrder"></div>
            </div>
          </div>
        </div>

        <div class="category-section">
          <div class="category-title"><div class="cat-icon" style="background:#fef2f2; color:var(--danger);">⚡</div>4. 性能与内容质量防护</div>
          <div class="two-col-row">
            <div class="spec-card">
              <div class="card-title">图片资源限制</div>
              <div class="size-input-wrap" style="margin: 16px 0;">
                <input class="field-input" type="number" v-model="config.imageSizeLimit" style="flex:1;">
                <span class="size-unit">KB</span>
              </div>
              <div class="switch-row" style="border-top:1px dashed var(--border); padding-top:16px;">
                <div class="switch-info"><div class="switch-name">优先推荐使用 WebP/AVIF</div></div>
                <div class="toggle" :class="{ on: config.webpCheck }" @click="config.webpCheck = !config.webpCheck"></div>
              </div>
            </div>
            
            <div class="spec-card">
              <div class="switch-row" style="border:none; padding:0; margin-bottom:20px; padding-top:6px;">
                <div class="switch-info"><div class="switch-name">占位符硬编码检测</div><div class="switch-desc">检测未经国际化处理的中文字符</div></div>
                <div class="toggle" :class="{ on: config.hardcodeCheck }" @click="config.hardcodeCheck = !config.hardcodeCheck"></div>
              </div>
              <div class="switch-row" style="border-top:1px dashed var(--border); padding-top:20px;">
                <div class="switch-info"><div class="switch-name">页面死链扫描</div><div class="switch-desc">检测 404 或失效的 URL 跳转</div></div>
                <div class="toggle" :class="{ on: config.deadlinkCheck }" @click="config.deadlinkCheck = !config.deadlinkCheck"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-show="mode === 'design'">
        <div class="design-section">
          <div class="spec-card">
            <div class="card-title"><span style="color:var(--primary); margin-right:6px;">📐</span> 对比区域设置 (全局模板)</div>
            <div class="switch-desc" style="margin-bottom: 24px;">指定走查时截图与设计稿的默认比对范围</div>
            
            <div class="compare-grid" style="background:var(--bg-sidebar); padding:20px; border-radius:var(--radius); margin-bottom:24px;">
              <div>
                <div class="field-label">截图宽度 (px)</div>
                <div class="size-input-wrap">
                  <input class="field-input" type="number" v-model="designConfig.compareWidth">
                  <span class="size-unit">px</span>
                </div>
              </div>
              <div>
                <div class="field-label">设备类型</div>
                <select class="spec-select" v-model="designConfig.deviceType">
                  <option value="desktop">桌面端 (Desktop)</option>
                  <option value="mobile">移动端 (Mobile)</option>
                  <option value="tablet">平板 (Tablet)</option>
                </select>
              </div>
            </div>

            <div class="slider-box" style="margin-top:0;">
              <div class="slider-header">
                <span class="slider-title">色差容忍阈值</span>
                <span class="slider-val">{{ designConfig.colorThreshold }}%</span>
              </div>
              <div class="slider-hint">数值越低，检测越严格；建议初始值 10%</div>
              <input type="range" min="0" max="100" v-model="designConfig.colorThreshold" class="custom-range">
            </div>
          </div>
        </div>

        <div class="design-section" style="margin-top:20px;">
          <div class="spec-card">
            <div class="card-title"><span style="color:var(--primary); margin-right:6px;">🤖</span> AI 智能分析</div>
            
            <div class="ai-item" style="background:var(--bg-sidebar); padding:16px 20px; border-radius:var(--radius) var(--radius) 0 0; border-bottom:1px solid var(--border); margin-top:16px;">
              <div class="switch-row" style="margin-bottom:6px;">
                <div class="switch-name">启用 AI 差异分析</div>
                <div class="toggle" :class="{ on: designConfig.aiAnalysis }" @click="designConfig.aiAnalysis = !designConfig.aiAnalysis"></div>
              </div>
              <div class="switch-desc">自动识别布局偏移、色值差异、组件缺失等问题并给出优化建议</div>
            </div>
            <div class="ai-item" style="background:var(--bg-sidebar); padding:16px 20px; border-radius:0 0 var(--radius) var(--radius);">
              <div class="switch-row" style="margin-bottom:6px;">
                <div class="switch-name">生成走查报告摘要</div>
                <div class="toggle" :class="{ on: designConfig.aiSummary }" @click="designConfig.aiSummary = !designConfig.aiSummary"></div>
              </div>
              <div class="switch-desc">走查完成后由 AI 自动生成一份可读性强的问题摘要报告</div>
            </div>
          </div>
        </div>

        <div class="design-section" style="margin-top:20px;">
          <div class="spec-card">
            <div class="card-title"><span style="color:var(--primary); margin-right:6px;">🎯</span> 对比精度与遮罩</div>
            
            <div class="field-label" style="margin:20px 0 12px;">对比模式 (Comparison Mode)</div>
            <div class="precision-tabs">
              <div class="precision-opt" :class="{ active: designConfig.precisionMode === 'pixel' }" @click="designConfig.precisionMode = 'pixel'">
                <div class="precision-radio"></div>
                <div>
                  <div class="precision-opt-name">像素级对比</div>
                  <div class="switch-desc">严格校验每一个像素的差异</div>
                </div>
              </div>
              <div class="precision-opt" :class="{ active: designConfig.precisionMode === 'visual' }" @click="designConfig.precisionMode = 'visual'">
                <div class="precision-radio"></div>
                <div>
                  <div class="precision-opt-name">视觉语义</div>
                  <div class="switch-desc">基于视觉感官忽略微小偏移</div>
                </div>
              </div>
            </div>

            <div class="ignore-grid" style="border-top:1px dashed var(--border); padding-top:24px; margin-top:24px;">
              <div>
                <div class="field-label" style="margin-bottom:16px;">忽略区域设置</div>
                <label class="checkbox-item"><input type="checkbox" v-model="designConfig.ignoreStatus"> 状态栏</label>
                <label class="checkbox-item"><input type="checkbox" v-model="designConfig.ignoreAds"> 动态广告位</label>
              </div>
              <div>
                <div class="field-label" style="margin-bottom:16px;">自动对齐锚点</div>
                <div class="anchor-grid">
                  <div v-for="i in 9" :key="i" class="anchor-dot" :class="{ active: designConfig.anchor === i - 1 }" @click="designConfig.anchor = i - 1"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import AppNavbar from '../components/AppNavbar.vue'
import { useAuditStore } from '../store/audit'
import { showMsg, showPrompt } from '../utils/modal'
import Swal from 'sweetalert2'

const router = useRouter()
const auditStore = useAuditStore()
const mode = ref('baseline')

// 默认基准配置：完全覆盖四项标准的细颗粒度设置
const defaultBaseline = {
  colors: [{ hex: '#256af4', label: '主品牌色' }, { hex: '#2f54eb', label: '辅助色' }],
  nearColorCheck: true, 
  colorTolerance: 15,
  fontFamily: 'PingFang SC, Microsoft YaHei', 
  lineHeights: '1.2, 1.5, 1.6',
  fontTokens: [12, 14, 16, 18, 20, 24, 32], 
  spacingTokens: [4, 8, 12, 16, 24, 32],
  gridCheck: true, 
  gridTokens: [8], 
  radiusTokens: [2, 4, 8, 12, 16],
  shadowCheck: true, 
  shadowPreset: 'ant', 
  minClickArea: 44, 
  hoverCheck: true,
  textOverflow: 'ellipsis', 
  responsiveCheck: true, 
  emptyStateCheck: true, 
  loadingStateCheck: true,
  imageSizeLimit: 500, 
  webpCheck: true, 
  hardcodeCheck: true, 
  deadlinkCheck: true,
  altCheck: true, 
  domSemantics: true, 
  focusOrder: true
}

const defaultDesign = {
  compareWidth: 1440, deviceType: 'desktop', colorThreshold: 10,
  aiAnalysis: true, aiSummary: true, precisionMode: 'pixel', ignoreStatus: true, ignoreAds: false, anchor: 0
}

const globalConf = auditStore.globalConfig || {}
const config = reactive(JSON.parse(JSON.stringify(globalConf.baseline || defaultBaseline)))
const designConfig = reactive(JSON.parse(JSON.stringify(globalConf.design || defaultDesign)))

// SweetAlert2 高级拾色器
const editColor = async (idx) => {
  const color = config.colors[idx]
  const { value: formValues } = await Swal.fire({
    title: '编辑品牌色',
    html: `
      <div style="text-align:left; margin-bottom:8px; font-size:0.9rem; color:var(--text-secondary); font-weight:600;">颜色名称</div>
      <input id="swal-input1" class="input-field" style="margin-bottom:20px; width:100%; box-sizing:border-box;" value="${color.label}">
      <div style="text-align:left; margin-bottom:8px; font-size:0.9rem; color:var(--text-secondary); font-weight:600;">色值 (HEX)</div>
      <div style="display:flex; align-items:center; gap:12px;">
        <input type="color" id="swal-input2" style="width:48px; height:48px; border:none; border-radius:var(--radius-sm); cursor:pointer; padding:0; background:none;" value="${color.hex}">
        <input id="swal-input3" class="input-field" style="flex:1; font-family:monospace;" value="${color.hex}">
      </div>
    `,
    focusConfirm: false, showCancelButton: true, confirmButtonText: '确定', cancelButtonText: '取消', confirmButtonColor: '#3b6ef8',
    didOpen: () => {
      const cp = document.getElementById('swal-input2'); const text = document.getElementById('swal-input3');
      cp.addEventListener('input', (e) => text.value = e.target.value)
      text.addEventListener('input', (e) => { if(/^#[0-9A-Fa-f]{6}$/i.test(e.target.value)) cp.value = e.target.value })
    },
    preConfirm: () => ({ label: document.getElementById('swal-input1').value, hex: document.getElementById('swal-input3').value })
  })
  if (formValues) {
    config.colors[idx].label = formValues.label
    config.colors[idx].hex = formValues.hex
  }
}

const addColor = () => config.colors.push({ hex: '#000000', label: '自定义色' })
const removeColor = (idx) => config.colors.splice(idx, 1)

const addToken = async (type) => {
  const val = await showPrompt('添加规范数值', '请输入数值 (px)')
  if (val && !isNaN(val)) {
    if (type === 'font') config.fontTokens.push(Number(val));
    else config[`${type}Tokens`].push(Number(val));
  }
}

const saveConfig = async () => {
  auditStore.saveGlobalConfig({ baseline: config, design: designConfig })
  await showMsg('成功', '全局规范模板已保存！', 'success')
  router.push('/')
}
</script>

<style scoped>
.page-container { background: var(--bg-page); min-height: 100vh; padding-top: var(--nav-height); }
.spec-page { max-width: 1080px; margin: 0 auto; padding: 30px 24px 60px; }

.breadcrumb { display: flex; align-items: center; gap: 8px; font-size: 0.88rem; color: var(--text-muted); margin-bottom: 24px; }
.breadcrumb a { color: var(--text-secondary); text-decoration: none; transition: var(--transition);}
.breadcrumb a:hover { color: var(--primary); }
.breadcrumb .cur { color: var(--text-primary); font-weight: 600; }

.spec-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
.spec-title { font-size: 1.7rem; font-weight: 800; color: var(--text-primary); margin-bottom: 6px; letter-spacing: -0.02em;}
.spec-subtitle { font-size: 0.9rem; color: var(--text-secondary); }
.spec-header-actions { display: flex; gap: 12px; }

.spec-tabs { display: flex; border-bottom: 2px solid var(--border); margin-bottom: 36px; }
.spec-tab { padding: 12px 28px; font-size: 1rem; font-weight: 500; color: var(--text-secondary); cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -2px; transition: var(--transition);}
.spec-tab.active { color: var(--primary); border-bottom-color: var(--primary); font-weight: 700; }

.category-section { margin-bottom: 40px; }
.category-title { display: flex; align-items: center; gap: 12px; font-size: 1.15rem; font-weight: 800; margin-bottom: 20px; color: var(--text-primary);}
.cat-icon { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 16px;}

.two-col-row { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px;}
.three-col-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 24px; margin-bottom: 24px;}
.four-col-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 24px;}

.spec-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 26px; box-shadow: var(--shadow-sm); transition: var(--transition);}
.spec-card:hover { border-color: #d1d5db; box-shadow: var(--shadow-md); }
.card-title { font-size: 1rem; font-weight: 700; margin-bottom: 16px; color: var(--text-primary); display: flex; align-items: center; gap: 8px;}
.card-title-sm { font-size: 0.9rem; font-weight: 700; color: var(--text-primary); }

.flex-center-card { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
.flex-between-card { display: flex; justify-content: space-between; align-items: flex-start; }

/* 颜色系统块 */
.color-row { display: flex; align-items: center; gap: 12px; padding: 12px 14px; border: 1px solid var(--border-light); border-radius: var(--radius-sm); margin-bottom: 10px; background: var(--bg-sidebar); cursor: pointer; transition: var(--transition);}
.color-row:hover { border-color: var(--primary); background: var(--bg-card); box-shadow: 0 4px 12px rgba(59,110,248,0.06);}
.color-swatch-sq { width: 26px; height: 26px; border-radius: 6px; border: 1px solid rgba(0,0,0,0.1); flex-shrink: 0;}
.color-edit-input { border: 1px solid transparent; background: transparent; padding: 4px 6px; font-size: 0.9rem; font-weight: 600; color: var(--text-primary); outline: none; border-radius: 4px; transition: var(--transition); flex: 1;}
.color-edit-input:hover, .color-edit-input:focus { border-color: var(--primary); background: white;}
.hex-font { font-family: monospace; color: var(--text-secondary); font-weight: 500; max-width: 85px;}
.color-del-btn { color: var(--text-muted); font-size: 1.2rem; transition: var(--transition); padding: 0 4px;}
.color-del-btn:hover { color: var(--danger); transform: scale(1.1);}
.add-color-row { border: 1.5px dashed var(--border); padding: 12px; text-align: center; border-radius: var(--radius-sm); font-size: 0.9rem; font-weight: 600; color: var(--text-secondary); cursor: pointer; margin-top: 14px; background: var(--bg-card); transition: var(--transition);}
.add-color-row:hover { background: var(--primary-light); color: var(--primary); border-color: var(--primary); }

/* 表单元素 */
.field-row { margin-bottom: 20px; }
.field-label { font-size: 0.8rem; font-weight: 700; color: var(--text-secondary); margin-bottom: 8px; letter-spacing: 0.02em;}
.field-input, .spec-select { width: 100%; padding: 12px 14px; border: 1.5px solid var(--border); border-radius: var(--radius-sm); font-size: 0.95rem; background: var(--bg-card); color: var(--text-primary); transition: var(--transition); box-sizing: border-box; }
.field-input:focus, .spec-select:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }
.spec-select { appearance: none; background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%239CA3AF%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E"); background-repeat: no-repeat; background-position: right 14px top 50%; background-size: 10px auto; }

/* 令牌系统 */
.token-row { display: flex; gap: 10px; flex-wrap: wrap; }
.token-pill { padding: 6px 12px; background: var(--primary-light); color: var(--primary); border-radius: 6px; font-size: 0.85rem; font-weight: 700; display:flex; align-items:center; gap:6px;}
.sq-tag { padding: 6px 12px; border: 1.5px solid var(--border); background: var(--bg-card); color: var(--text-primary); border-radius: 6px; font-size: 0.85rem; font-weight: 600; display:flex; align-items:center; gap:6px;}
.rm { cursor: pointer; color: var(--text-muted); font-size: 14px; font-weight: 400;}
.rm:hover { color: var(--danger); }
.token-add-btn, .input-add-btn { padding: 6px 14px; border: 1.5px dashed var(--border); border-radius: 6px; font-size: 0.85rem; font-weight: 600; color: var(--text-secondary); cursor: pointer; background: var(--bg-card); transition: var(--transition);}
.token-add-btn:hover, .input-add-btn:hover { border-color: var(--primary); color: var(--primary); background: var(--primary-light); }

/* 滑动条系统 */
.slider-box { margin-top: 20px; padding: 16px; background: var(--bg-sidebar); border-radius: var(--radius-sm); border: 1px solid var(--border-light);}
.slider-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.slider-title { font-size: 0.85rem; font-weight: 700; color: var(--text-primary); }
.slider-val { font-size: 1rem; font-weight: 800; color: var(--primary); }
.custom-range { appearance: none; -webkit-appearance: none; width: 100%; height: 6px; background: var(--border); border-radius: 99px; outline: none; margin-top: 10px; }
.custom-range::-webkit-slider-thumb { -webkit-appearance: none; width: 18px; height: 18px; border-radius: 50%; background: white; border: 3px solid var(--primary); cursor: pointer; box-shadow: var(--shadow-sm); }

/* 开关与文本块 */
.switch-row { display: flex; justify-content: space-between; align-items:flex-start;}
.switch-name { font-size: 0.95rem; font-weight: 700; color: var(--text-primary); }
.toggle { width: 44px; height: 24px; background: var(--border); border-radius: 99px; position: relative; cursor: pointer; transition: var(--transition); flex-shrink: 0;}
.toggle.on { background: var(--primary); }
.toggle::after { content: ''; position: absolute; width: 18px; height: 18px; background: white; border-radius: 50%; top: 3px; left: 3px; transition: var(--transition); box-shadow: var(--shadow-sm);}
.toggle.on::after { left: 23px; }

.hotzone-row { display: flex; justify-content: space-between; align-items: center; }
.hotzone-label { font-size: 0.95rem; color: var(--text-primary); font-weight: 700;}
.hotzone-val { width: 64px; padding: 8px; border: 1.5px solid var(--border); border-radius: var(--radius-sm); font-size: 1.05rem; font-weight: 800; text-align: center; color: var(--primary); outline: none; }
.hotzone-val:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }

.big-val { font-size: 2.4rem; font-weight: 900; color: var(--primary); line-height: 1; margin: 16px 0;}
.size-input-wrap { display: flex; align-items: center; gap: 10px; }
.size-unit { font-size: 0.9rem; font-weight: 700; color: var(--text-secondary);}

/* 对比模式卡片 (Design Mode) */
.precision-tabs { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
.precision-opt { border: 2px solid var(--border); border-radius: var(--radius); padding: 20px; cursor: pointer; display: flex; gap: 16px; transition: var(--transition);}
.precision-opt.active { border-color: var(--primary); background: var(--primary-light); }
.precision-radio { width: 20px; height: 20px; border-radius: 50%; border: 2px solid var(--text-muted); flex-shrink: 0; margin-top: 2px; }
.precision-opt.active .precision-radio { border-color: var(--primary); background: var(--primary); box-shadow: inset 0 0 0 4px white; }
.precision-opt-name { font-size: 1rem; font-weight: 800; color: var(--text-primary); margin-bottom: 6px;}

.ignore-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; }
.checkbox-item { display: flex; align-items: center; gap: 10px; font-size: 0.95rem; color: var(--text-primary); font-weight: 500; margin-bottom: 12px; cursor: pointer;}
.checkbox-item input { width: 18px; height: 18px; accent-color: var(--primary);}

.anchor-grid { display: grid; grid-template-columns: repeat(3, 40px); grid-template-rows: repeat(3, 40px); gap: 8px; }
.anchor-dot { width: 40px; height: 40px; border: 2px solid var(--border); border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; background: var(--bg-sidebar); transition: var(--transition);}
.anchor-dot.active { background: var(--primary); border-color: var(--primary); }
.anchor-dot.active::after { content: ''; width: 10px; height: 10px; background: white; border-radius: 50%; }
</style>