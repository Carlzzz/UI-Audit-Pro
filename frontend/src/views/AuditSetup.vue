<template>
  <div class="page-container">
    <AppNavbar variant="full" active-key="scan" />

    <div class="spec-page">
      <div class="breadcrumb">
        <span>🏠</span>
        <a href="#" @click.prevent="$router.push('/')">首页</a>
        <span class="sep">›</span>
        <span class="cur">确认本次走查规范</span>
      </div>

      <div class="spec-header">
        <div>
          <div class="spec-title">确认本次走查规范</div>
          <div class="spec-subtitle">已自动代入全局模板，您可针对本次任务进行临时调整（修改不影响全局配置）</div>
        </div>
        <div class="spec-header-actions">
          <button class="btn btn-ghost" @click="$router.push('/')">取消</button>
          <button
            class="btn btn-primary"
            :disabled="mode === 'design' && !isDesignResourceReady"
            @click="startScan"
          >
            ⚡ 开始走查
          </button>
        </div>
      </div>

      <div class="spec-tabs">
        <div class="spec-tab" :class="{ active: mode === 'baseline' }" @click="mode = 'baseline'">⇌ 基准值模式</div>
        <div class="spec-tab" :class="{ active: mode === 'design' }" @click="mode = 'design'">🖼 设计稿模式</div>
      </div>

      <div v-show="mode === 'baseline'">
        <div class="category-section">
          <div class="category-title"><div class="cat-icon blue">✨</div>1. 视觉一致性标准</div>
          
          <div class="two-col-row">
            <div class="spec-card">
              <div class="card-title">◎ 品牌色盘与近色检测 (本次)</div>
              <div id="color-list" style="margin-top:15px;">
                <div class="color-row" v-for="(color, idx) in taskConfig.colors" :key="idx" @click="editColor(idx)">
                  <div class="color-swatch-sq" :style="{ background: color.hex }"></div>
                  <input type="text" class="color-edit-input" v-model="color.label" title="点击修改" @click.stop />
                  <input type="text" class="color-edit-input hex-font" v-model="color.hex" title="点击修改" @click.stop />
                  <button class="color-del-btn" @click.stop="removeColor(idx)">🗑</button>
                </div>
              </div>
              <div class="add-color-row" @click="addColor"><span>＋</span> 添加临时色值</div>
              <div class="switch-row" style="margin-top:14px; border-top:1px dashed #e8eaf0; padding-top:14px;">
                <div class="switch-info"><div class="switch-name">自动检测并标记色彩误差</div></div>
                <div class="toggle" :class="{ on: taskConfig.nearColorCheck }" @click="taskConfig.nearColorCheck = !taskConfig.nearColorCheck"></div>
              </div>
              <div v-show="taskConfig.nearColorCheck" style="margin-top: 16px;">
                <div class="cg-label" style="display:flex; justify-content:space-between; margin-bottom:6px;">
                    <span style="font-size:0.85rem; font-weight:600; color:#4b5563;">色差容忍阈值</span>
                    <span style="color:#3b6ef8; font-weight:700;">{{ taskConfig.colorTolerance }}</span>
                </div>
                <input type="range" min="0" max="50" v-model="taskConfig.colorTolerance" style="width:100%; height:4px; accent-color: #3b6ef8;">
              </div>
            </div>

            <div class="spec-card">
              <div class="card-title">Tr 字体与排版系统 (本次)</div>
              <div class="field-row" style="margin-top:10px;">
                <div class="field-label">字体族</div>
                <input class="field-input" type="text" v-model="taskConfig.fontFamily">
              </div>
              <div class="field-row">
                <div class="field-label">行高基数</div>
                <input class="field-input" type="text" v-model="taskConfig.lineHeights">
              </div>
              <div class="field-row">
                <div class="field-label" style="text-transform:uppercase;">允许的字阶 (FONT SIZES)</div>
                <div class="token-row">
                  <span class="token-pill" v-for="(t, idx) in taskConfig.fontTokens" :key="idx">{{ t }}px <span class="rm" @click="taskConfig.fontTokens.splice(idx,1)">×</span></span>
                  <span class="token-add-btn" @click="addToken('font')">＋ 添加</span>
                </div>
              </div>
            </div>
          </div>

          <div class="two-col-row">
            <div class="spec-card">
              <div class="card-title">⊞ 间距与栅格</div>
              <div class="field-row" style="margin-top:10px;">
                <div class="field-label" style="text-transform:uppercase;">间距令牌 (SPACING TOKENS)</div>
                <div class="token-row" style="margin-bottom:20px;">
                  <span class="token-pill" v-for="(t, idx) in taskConfig.spacingTokens" :key="idx">{{ t }}px <span class="rm" @click="taskConfig.spacingTokens.splice(idx,1)">×</span></span>
                  <span class="token-add-btn" @click="addToken('spacing')">＋ 添加</span>
                </div>
              </div>
              <div class="switch-row" style="border-top:1px dashed #e8eaf0; padding-top:16px;">
                <div class="switch-name">栅格对齐检测 (px)</div>
                <div class="toggle" :class="{ on: taskConfig.gridCheck }" @click="taskConfig.gridCheck = !taskConfig.gridCheck"></div>
              </div>
              <div class="token-row" style="margin-top:10px;" v-show="taskConfig.gridCheck">
                <span class="sq-tag" v-for="(g, idx) in taskConfig.gridTokens" :key="idx">{{ g }}px <span class="rm" @click="taskConfig.gridTokens.splice(idx,1)">🗑</span></span>
                <span class="input-add-btn" @click="addToken('grid')">＋ 增加</span>
              </div>
            </div>

            <div class="spec-card">
              <div class="card-title">◈ 圆角与投影</div>
              <div class="field-row" style="margin-top:10px;">
                <div class="field-label" style="text-transform:uppercase;">圆角规范 (BORDER RADIUS)</div>
                <div class="token-row" style="margin-bottom:20px;">
                  <span class="sq-tag" v-for="(r, idx) in taskConfig.radiusTokens" :key="idx">{{ r }}px <span class="rm" @click="taskConfig.radiusTokens.splice(idx,1)">🗑</span></span>
                  <span class="input-add-btn" @click="addToken('radius')">＋ 增加</span>
                </div>
              </div>
              <div class="switch-row" style="border-top: 1px dashed #e8eaf0; padding-top:16px; margin-bottom:12px;">
                <div class="switch-info"><div class="switch-name">阴影规范检测</div></div>
                <div class="toggle" :class="{ on: taskConfig.shadowCheck }" @click="taskConfig.shadowCheck = !taskConfig.shadowCheck"></div>
              </div>
              <div class="field-row" v-show="taskConfig.shadowCheck">
                <div class="field-label">投影预设</div>
                <select class="spec-select" v-model="taskConfig.shadowPreset">
                  <option value="ant">符合 Ant Design 投影规范</option>
                  <option value="material">符合 Material Design 投影规范</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <div class="category-section">
          <div class="category-title"><div class="cat-icon blue" style="background:#eff6ff;color:#3b82f6;">👆</div>2. 交互与布局标准</div>
          <div class="three-col-row">
            <div class="spec-card">
              <div class="card-title" style="font-size:0.9rem;">点击区域与状态</div>
              <div class="hotzone-row" style="margin: 20px 0;"><div class="hotzone-label">最小点击热区</div><div style="display:flex; align-items:center; gap:5px;"><input class="hotzone-val" type="number" v-model="taskConfig.minClickArea"> px</div></div>
              <div class="switch-row" style="border-top:1px dashed #e8eaf0; padding-top:14px;"><div class="switch-info"><div class="switch-name">组件触发状态</div></div><div class="toggle" :class="{ on: taskConfig.hoverCheck }" @click="taskConfig.hoverCheck = !taskConfig.hoverCheck"></div></div>
            </div>
            <div class="spec-card">
              <div class="card-title" style="font-size:0.9rem;">文本溢出与响应式</div>
              <div class="field-row" style="margin:14px 0 16px;"><select class="spec-select" v-model="taskConfig.textOverflow"><option value="ellipsis">默认使用省略号</option><option value="wrap">换行显示</option></select></div>
              <div class="switch-row" style="border-top:1px dashed #e8eaf0; padding-top:14px;"><div class="switch-info"><div class="switch-name">响应式适配检测</div></div><div class="toggle" :class="{ on: taskConfig.responsiveCheck }" @click="taskConfig.responsiveCheck = !taskConfig.responsiveCheck"></div></div>
            </div>
            <div class="spec-card">
              <div class="card-title" style="font-size:0.9rem;">异常状态覆盖</div>
              <div class="switch-row" style="border:none; padding:0; margin-top:14px;"><div class="switch-info"><div class="switch-name">空状态覆盖</div></div><div class="toggle" :class="{ on: taskConfig.emptyStateCheck }" @click="taskConfig.emptyStateCheck = !taskConfig.emptyStateCheck"></div></div>
              <div class="switch-row" style="padding-top:14px;"><div class="switch-info"><div class="switch-name">加载状态预设</div></div><div class="toggle" :class="{ on: taskConfig.loadingStateCheck }" @click="taskConfig.loadingStateCheck = !taskConfig.loadingStateCheck"></div></div>
            </div>
          </div>
        </div>

        <div class="category-section">
          <div class="category-title"><div class="cat-icon blue" style="background:#e0e7ff;color:#2563eb;">♿</div>3. 无障碍与合规性</div>
          <div class="four-col-row">
            <div class="spec-card" style="padding:18px;"><div class="card-title" style="font-size:0.85rem; margin-bottom:12px; color:#6b7280;">色彩对比度阈值</div><div class="big-val">4.5:1</div><div class="aa-badge">AA级标准</div></div>
            <div class="spec-card" style="padding:18px;"><div class="card-title" style="font-size:0.85rem; margin-bottom:8px;">图片 Alt 属性</div><div class="toggle" :class="{ on: taskConfig.altCheck }" @click="taskConfig.altCheck = !taskConfig.altCheck" style="margin-top:10px;"></div></div>
            <div class="spec-card" style="padding:18px;"><div class="card-title" style="font-size:0.85rem; margin-bottom:8px;">DOM 语义化</div><div class="toggle" :class="{ on: taskConfig.domSemantics }" @click="taskConfig.domSemantics = !taskConfig.domSemantics" style="margin-top:10px;"></div></div>
            <div class="spec-card" style="padding:18px;"><div class="card-title" style="font-size:0.85rem; margin-bottom:8px;">焦点顺序逻辑</div><div class="toggle" :class="{ on: taskConfig.focusOrder }" @click="taskConfig.focusOrder = !taskConfig.focusOrder" style="margin-top:10px;"></div></div>
          </div>
        </div>

        <div class="category-section">
          <div class="category-title"><div class="cat-icon blue" style="background:#fce7f3;color:#4f46e5;">⚡</div>4. 性能与内容质量</div>
          <div class="two-col-row">
            <div class="spec-card">
              <div class="card-title">图片资源限制</div>
              <div class="size-input-wrap" style="margin-bottom:16px;"><input class="size-input-wide" type="number" v-model="taskConfig.imageSizeLimit"><span class="size-unit">KB</span></div>
              <div class="switch-row" style="border-top:1px dashed #e8eaf0; padding-top:14px;"><div class="switch-info"><div class="switch-name">优先推荐使用 WebP/AVIF</div></div><div class="toggle" :class="{ on: taskConfig.webpCheck }" @click="taskConfig.webpCheck = !taskConfig.webpCheck"></div></div>
            </div>
            <div class="spec-card">
              <div class="switch-row" style="border:none; padding:0; margin-bottom:20px;"><div class="switch-info"><div class="switch-name" style="font-size:0.95rem;">占位符硬编码检测</div></div><div class="toggle" :class="{ on: taskConfig.hardcodeCheck }" @click="taskConfig.hardcodeCheck = !taskConfig.hardcodeCheck"></div></div>
              <div class="switch-row" style="border-top:1px dashed #e8eaf0; padding-top:20px;"><div class="switch-info"><div class="switch-name" style="font-size:0.95rem;">页面死链扫描</div></div><div class="toggle" :class="{ on: taskConfig.deadlinkCheck }" @click="taskConfig.deadlinkCheck = !taskConfig.deadlinkCheck"></div></div>
            </div>
          </div>
        </div>
      </div>

      <div v-show="mode === 'design'">
        <div class="design-section">
          <div class="design-card">
            <div class="design-card-title"><span style="color:#3b6ef8; margin-right:6px;">🔗</span> 设计资源接入</div>
            <div class="field-label" style="margin-top:12px; margin-bottom:8px;">Figma 文件链接或其它设计系统页面 URL（需包含具体画板/组件 node-id）</div>
            <div class="url-input-wrap">
              <input class="url-input" type="url" v-model="taskDesignConfig.url" placeholder="https://www.figma.com/file/...">
              <button class="btn btn-primary" style="white-space:nowrap; padding: 0 20px;" @click="parseFigma">解析资源</button>
            </div>
            <div class="url-input-actions">
              <button
                class="icon-btn"
                :disabled="!taskDesignConfig.localImageBase64"
                @click.stop="zoomIn"
              >
                🔍 放大
              </button>
              <button
                class="icon-btn"
                :disabled="!taskDesignConfig.localImageBase64"
                @click.stop="zoomOut"
              >
                🔎 缩小
              </button>
              <button
                class="icon-btn"
                :disabled="!taskDesignConfig.localImageBase64"
                @click.stop="resetThumbZoom"
              >
                ⛶ 适应屏幕
              </button>
            </div>
            
            <input type="file" ref="fileInput" style="display: none" accept="image/png, image/jpeg" @change="onFileChange">
            <div class="upload-area" @click="triggerUpload" @dragover.prevent @dragenter.prevent @drop.prevent="onFileDrop">
              <template v-if="taskDesignConfig.localImageBase64">
                <img
                  class="upload-thumb"
                  :style="{ transform: `scale(${thumbZoom})` }"
                  :src="`data:image/png;base64,${taskDesignConfig.localImageBase64}`"
                  alt="本地设计稿预览"
                >
                <div class="upload-text">
                  已上传：{{ taskDesignConfig.localFileName || '本地设计稿' }}
                </div>
                <div class="upload-hint">点击或拖拽可重新上传其它 PNG / JPG 图片</div>
              </template>
              <template v-else>
                <div class="upload-icon">☁</div>
                <div class="upload-text">拖拽本地设计稿图片到此处或 <span style="color:#3b6ef8; cursor:pointer;">点击上传</span></div>
                <div class="upload-hint">支持 PNG / JPG 图片（单张不超过 20MB）</div>
              </template>
            </div>
          </div>
        </div>

        <div class="design-section">
          <div class="design-card">
            <div class="design-card-title"><span style="color:#3b6ef8; margin-right:6px;">📐</span> 对比区域设置</div>
            <div class="design-card-hint">指定走查时截图与设计稿的比对范围</div>
            
            <div class="compare-grid" style="background:#f9fafb; padding:16px; border-radius:8px; margin-bottom:20px;">
              <div>
                <div class="cg-label">截图宽度 (px)</div>
                <div class="size-input-wrap">
                  <input class="size-input-wide" type="number" v-model="taskDesignConfig.compareWidth">
                  <span class="size-unit">px</span>
                </div>
              </div>
              <div>
                <div class="cg-label">设备类型</div>
                <select class="spec-select" v-model="taskDesignConfig.deviceType">
                  <option value="desktop">桌面端 (Desktop)</option>
                  <option value="mobile">移动端 (Mobile)</option>
                  <option value="tablet">平板 (Tablet)</option>
                </select>
              </div>
            </div>

            <div>
              <div class="cg-label">色差容忍阈值</div>
              <div class="slider-label-row">
                <div class="slider-hint">数值越低，检测越严格；建议初始值 10%</div>
                <div class="slider-val">{{ taskDesignConfig.colorThreshold }}%</div>
              </div>
              <input type="range" min="0" max="100" v-model="taskDesignConfig.colorThreshold" style="width:100%; height:4px; accent-color: #3b6ef8;">
            </div>
          </div>
        </div>

        <div class="design-section">
          <div class="design-card">
            <div class="design-card-title"><span style="color:#3b6ef8; margin-right:6px;">🤖</span> AI 智能分析</div>
            <div class="design-card-hint">开启后将调用 AI 模型对差异区域进行语义化分析和建议</div>
            
            <div class="ai-item" style="background:#f9fafb; padding:16px; border-radius:8px 8px 0 0; border-bottom:1px solid #e8eaf0;">
              <div class="ai-item-header">
                <div class="ai-item-name">启用 AI 差异分析</div>
                <div class="toggle" :class="{ on: taskDesignConfig.aiAnalysis }" @click="taskDesignConfig.aiAnalysis = !taskDesignConfig.aiAnalysis"></div>
              </div>
              <div class="ai-item-desc">自动识别布局偏移、色值差异、组件缺失等问题并给出优化建议</div>
            </div>
            <div class="ai-item" style="background:#f9fafb; padding:16px; border-radius:0 0 8px 8px; border-top:none;">
              <div class="ai-item-header">
                <div class="ai-item-name">生成走查报告摘要</div>
                <div class="toggle" :class="{ on: taskDesignConfig.aiSummary }" @click="taskDesignConfig.aiSummary = !taskDesignConfig.aiSummary"></div>
              </div>
              <div class="ai-item-desc">走查完成后由 AI 自动生成一份可读性强的问题摘要报告</div>
            </div>
          </div>
        </div>

        <div class="design-section">
          <div class="design-card">
            <div class="design-card-title"><span style="color:#3b6ef8; margin-right:6px;">🎯</span> 对比精度设置</div>
            <div style="font-size:0.85rem; font-weight:600; color:#1a1d2e; margin-top:16px; margin-bottom:12px;">对比模式 (Comparison Mode)</div>
            
            <div class="precision-tabs">
              <div class="precision-opt" :class="{ active: taskDesignConfig.precisionMode === 'pixel' }" @click="taskDesignConfig.precisionMode = 'pixel'">
                <div class="precision-radio"></div>
                <div>
                  <div class="precision-opt-name">像素级对比</div>
                  <div class="precision-opt-desc">严格校验每一个像素的差异</div>
                </div>
              </div>
              <div class="precision-opt" :class="{ active: taskDesignConfig.precisionMode === 'visual' }" @click="taskDesignConfig.precisionMode = 'visual'">
                <div class="precision-radio"></div>
                <div>
                  <div class="precision-opt-name">视觉语义</div>
                  <div class="precision-opt-desc">基于视觉感官忽略微小偏移</div>
                </div>
              </div>
            </div>

            <div class="ignore-grid" style="border-top:1px dashed #e8eaf0; padding-top:20px; margin-top:20px;">
              <div>
                <div class="check-group-title">忽略区域设置</div>
                <label class="checkbox-item"><input type="checkbox" v-model="taskDesignConfig.ignoreStatus"> 状态栏</label>
                <label class="checkbox-item"><input type="checkbox" v-model="taskDesignConfig.ignoreAds"> 动态广告位</label>
              </div>
              <div>
                <div class="check-group-title">自动对齐锚点</div>
                <div class="anchor-grid">
                  <div v-for="i in 9" :key="i" class="anchor-dot" :class="{ active: taskDesignConfig.anchor === i - 1 }" @click="taskDesignConfig.anchor = i - 1"></div>
                </div>
                <div style="font-size:0.75rem; color:#9ca3af; margin-top:8px;">选择对比起始对齐位置</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import AppNavbar from '../components/AppNavbar.vue'
import { useAuditStore } from '../store/audit'
import { showMsg, showPrompt } from '../utils/modal'
import Swal from 'sweetalert2'

const router = useRouter()
const auditStore = useAuditStore()
const mode = ref(auditStore.checkMode || 'baseline')

const defaultBaseline = {
  colors: [{ hex: '#256af4', label: '主品牌色' }, { hex: '#2f54eb', label: '辅助色' }],
  nearColorCheck: true, colorTolerance: 15,
  fontFamily: 'PingFang SC, Microsoft YaHei', lineHeights: '1.2, 1.5, 1.6',
  fontTokens: [12, 14, 16, 18, 20, 24, 32], spacingTokens: [4, 8, 12, 16, 24, 32],
  gridTokens: [8], gridCheck: true, radiusTokens: [2, 4, 8, 12, 16],
  shadowCheck: true, shadowPreset: 'ant', minClickArea: 44, hoverCheck: true,
  textOverflow: 'ellipsis', responsiveCheck: true, emptyStateCheck: true, loadingStateCheck: true,
  imageSizeLimit: 500, webpCheck: true, hardcodeCheck: true, deadlinkCheck: true,
  altCheck: true, domSemantics: true, focusOrder: true
}

const defaultDesign = {
  url: '', compareWidth: 1440, deviceType: 'desktop', colorThreshold: 10,
  aiAnalysis: true, aiSummary: true, precisionMode: 'pixel', ignoreStatus: true, ignoreAds: false, anchor: 0,
  localImageBase64: '', localFileName: ''
}

const globalConf = auditStore.globalConfig || {}
const taskConfig = reactive(JSON.parse(JSON.stringify(globalConf.baseline || defaultBaseline)))
const taskDesignConfig = reactive(JSON.parse(JSON.stringify(globalConf.design || defaultDesign)))

const editColor = async (idx) => {
  const color = taskConfig.colors[idx]
  const { value: formValues } = await Swal.fire({
    title: '临时修改品牌色',
    html: `
      <div style="text-align:left; margin-bottom:8px; font-size:0.9rem; color:#4b5563;">颜色名称</div>
      <input id="swal-input1" class="swal2-input" style="margin:0; width:100%; box-sizing:border-box;" value="${color.label}">
      <div style="text-align:left; margin-top:20px; margin-bottom:8px; font-size:0.9rem; color:#4b5563;">色值 (HEX)</div>
      <div style="display:flex; align-items:center; gap:10px;">
        <input type="color" id="swal-input2" style="width:46px; height:46px; border:1px solid #e5e7eb; border-radius:6px; cursor:pointer; padding:0; background:none;" value="${color.hex}">
        <input id="swal-input3" class="swal2-input" style="margin:0; flex:1; font-family:monospace;" value="${color.hex}">
      </div>
    `,
    focusConfirm: false, showCancelButton: true, confirmButtonText: '确认', confirmButtonColor: '#3b6ef8',
    didOpen: () => {
      const cp = document.getElementById('swal-input2'); const text = document.getElementById('swal-input3');
      cp.addEventListener('input', (e) => text.value = e.target.value)
      text.addEventListener('input', (e) => { if(/^#[0-9A-Fa-f]{6}$/i.test(e.target.value)) cp.value = e.target.value })
    },
    preConfirm: () => ({ label: document.getElementById('swal-input1').value, hex: document.getElementById('swal-input3').value })
  })
  if (formValues) {
    taskConfig.colors[idx].label = formValues.label
    taskConfig.colors[idx].hex = formValues.hex
  }
}

const addColor = () => taskConfig.colors.push({ hex: '#000000', label: '临时色' })
const removeColor = (idx) => taskConfig.colors.splice(idx, 1)

const addToken = async (type) => {
  const val = await showPrompt('添加规范数值', '请输入数值 (px)')
  if (val && !isNaN(val)) {
    if (type === 'font') taskConfig.fontTokens.push(Number(val));
    else taskConfig[`${type}Tokens`].push(Number(val));
  }
}

// Figma 链接正则（与后端保持一致：必须包含 file/design + node-id）
const FIGMA_URL_REG = /figma\.com\/(?:file|design)\/([a-zA-Z0-9]+).*[\?&]node-id=([^&]+)/i

// 设计稿解析交互（前端先做格式校验，再给出更真实的反馈）
const parseFigma = () => {
  const url = (taskDesignConfig.url || '').trim()
  if (!url) return showMsg('提示', '请先输入 Figma 链接', 'warning')

  if (!FIGMA_URL_REG.test(url)) {
    return showMsg(
      '链接格式异常',
      '当前链接缺少 file/design 或 node-id 参数，请从 Figma 中复制具体画板/组件的分享链接（包含 node-id）。',
      'warning'
    )
  }

  Swal.fire({
    icon: 'success',
    title: '格式校验通过',
    text: '已确认该链接包含有效的 file/design 与 node-id。实际拉取设计稿将于走查时进行，如 Token 权限或网络异常仍可能解析失败。',
    confirmButtonColor: '#3b6ef8'
  })
}

// 本地缩略图缩放控制
const thumbZoom = ref(1)
const zoomStep = 0.15
const resetThumbZoom = () => { thumbZoom.value = 1 }
const zoomIn = () => { thumbZoom.value += zoomStep }
const zoomOut = () => { thumbZoom.value = Math.max(0.15, thumbZoom.value - zoomStep) }

// 本地文件上传逻辑
const fileInput = ref(null)
const triggerUpload = () => { if (fileInput.value) fileInput.value.click() }

const processFile = (file) => {
  if (!file) return
  // 基本类型及大小校验（与 UI 文案对齐）
  const acceptTypes = ['image/png', 'image/jpeg']
  const maxSize = 20 * 1024 * 1024 // 20MB

  if (!acceptTypes.includes(file.type)) {
    showMsg('不支持的文件类型', '仅支持 PNG / JPG 图片，请导出设计稿后再上传。', 'warning')
    return
  }

  if (file.size > maxSize) {
    showMsg('文件过大', '单张设计稿建议控制在 20MB 以内，请压缩或切片后再尝试。', 'warning')
    return
  }

  Swal.fire({ title: '正在读取设计稿', text: file.name, allowOutsideClick: false, didOpen: () => Swal.showLoading() })
  
  const reader = new FileReader()
  reader.onload = (e) => {
    const base64Str = e.target.result.split(',')[1]
    setTimeout(() => {
      taskDesignConfig.localFileName = file.name
      taskDesignConfig.localImageBase64 = base64Str
      taskDesignConfig.url = '' // 清空 Figma URL
      Swal.fire({ icon: 'success', title: '读取成功', text: '本地设计稿已就绪！', confirmButtonColor: '#3b6ef8' })
    }, 600)
  }
  reader.onerror = () => Swal.fire('读取失败', '无法读取文件', 'error')
  reader.readAsDataURL(file)
}
const onFileChange = (e) => { processFile(e.target.files[0]); e.target.value = '' }
const onFileDrop = (e) => { processFile(e.dataTransfer.files[0]) }

// 设计稿模式下资源是否就绪：有合法 Figma 链接或已上传本地图片
const isDesignResourceReady = computed(() => {
  if (mode.value !== 'design') return true
  if (taskDesignConfig.localImageBase64) return true

  const url = (taskDesignConfig.url || '').trim()
  if (!url) return false
  return FIGMA_URL_REG.test(url)
})

const startScan = () => {
  // 仅在设计稿模式下做额外校验，避免“空配置”触发后端错误
  if (mode.value === 'design' && !isDesignResourceReady.value) {
    return showMsg(
      '设计稿未就绪',
      '请先上传 PNG/JPG 设计稿图片，或填写包含 node-id 的 Figma 链接，再开始走查。',
      'warning'
    )
  }

  auditStore.setCheckMode(mode.value)
  auditStore.setTaskConfig(mode.value === 'baseline' ? taskConfig : taskDesignConfig)
  router.push('/scan')
}
</script>

<style scoped>
.page-container { background: #fbfcfd; min-height: 100vh; padding-top: 60px; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif;}
.spec-page { max-width: 960px; margin: 0 auto; padding: 20px 24px 40px; }
.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.85rem; color: #6b7280; margin-bottom: 24px; }
.breadcrumb a { color: #6b7280; text-decoration: none; }
.breadcrumb .cur { color: #1a1d2e; font-weight: 500; }
.spec-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.spec-title { font-size: 1.6rem; font-weight: 700; color: #1a1d2e; margin-bottom: 4px; }
.spec-subtitle { font-size: 0.88rem; color: #6b7280; }
.btn { border: none; padding: 9px 20px; border-radius: 8px; font-size: 0.9rem; cursor: pointer; font-weight: 600;}
.btn-primary { background: #3b6ef8; color: white; }
.btn-primary:hover { background: #256af4; }
.btn-ghost { background: transparent; color: #6b7280; border: 1px solid #e5e7eb; margin-right: 12px;}
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; background: #9ca3af; }

.spec-tabs { display: flex; border-bottom: 1px solid #e5e7eb; margin-bottom: 28px; }
.spec-tab { padding: 12px 24px 12px 0; font-size: 0.95rem; font-weight: 500; color: #6b7280; cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -1px; }
.spec-tab.active { color: #3b6ef8; border-bottom-color: #3b6ef8; font-weight: 600; }

.category-section { margin-bottom: 32px; }
.category-title { display: flex; align-items: center; gap: 10px; font-size: 1.05rem; font-weight: 700; margin-bottom: 16px; color:#1a1d2e;}
.cat-icon { width: 28px; height: 28px; border-radius: 6px; display: flex; align-items: center; justify-content: center; }
.two-col-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;}
.three-col-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 20px;}
.four-col-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px;}

.spec-card { background: white; border: 1px solid #e8eaf0; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
.card-title { font-size: 0.95rem; font-weight: 700; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;}

.color-row { display: flex; align-items: center; gap: 12px; padding: 10px 12px; border: 1px solid #f0f1f5; border-radius: 8px; margin-bottom: 8px; background:#fafbfd; cursor: pointer; transition: all 0.2s;}
.color-row:hover { border-color: #3b6ef8; background: #fff; box-shadow: 0 2px 8px rgba(59,110,248,0.08);}
.color-swatch-sq { width: 24px; height: 24px; border-radius: 4px; border: 1px solid rgba(0,0,0,0.1);}
.color-label { font-size: 0.85rem; font-weight: 600; flex: 1; color:#1a1d2e;}
.color-hex { font-size: 0.8rem; color: #6b7280; font-family: monospace; }
.color-del-btn { background: none; border: none; color: #9ca3af; cursor: pointer; font-size: 1.1rem; padding: 0 4px;}
.color-del-btn:hover { color: #ef4444; }
.add-color-row { border: 1px dashed #d1d5db; padding: 10px; text-align: center; border-radius: 8px; font-size: 0.85rem; color: #6b7280; cursor: pointer; margin-top: 12px; background:#fff;}
.add-color-row:hover { background: #f0f4ff; color: #3b6ef8; border-color: #3b6ef8; }

.color-edit-input { border: 1px solid transparent; background: transparent; padding: 4px 6px; font-size: 0.85rem; font-weight: 600; color: #1a1d2e; outline: none; border-radius: 4px; transition: all 0.2s; flex: 1;}
.color-edit-input:hover, .color-edit-input:focus { border-color: #3b6ef8; background: white;}
.hex-font { font-family: monospace; color: #6b7280; font-weight: normal; max-width: 80px;}

.field-row { margin-bottom: 16px; }
.field-label { font-size: 0.78rem; color: #6b7280; margin-bottom: 6px; font-weight: 500;}
.field-input { width: 100%; padding: 10px 12px; border: 1px solid #e2e4ec; border-radius: 8px; font-size: 0.9rem; outline: none; box-sizing: border-box;}
.field-input:focus { border-color: #3b6ef8; }

.token-row { display: flex; gap: 8px; flex-wrap: wrap; }
.token-pill, .sq-tag { padding: 4px 10px; border-radius: 6px; font-size: 0.82rem; font-weight: 600; display:flex; align-items:center; gap:4px;}
.token-pill { background: #eef2ff; color: #3b6ef8; }
.sq-tag { border: 1px solid #e2e4ec; background: white; color: #1a1d2e;}
.rm { cursor: pointer; color: #9ca3af; font-size:12px; margin-left:2px;}
.rm:hover { color: #ef4444; }
.token-add-btn, .input-add-btn { padding: 4px 12px; border: 1px dashed #d1d5db; border-radius: 6px; font-size: 0.82rem; color: #6b7280; cursor: pointer; background:white;}
.token-add-btn:hover, .input-add-btn:hover { border-color: #3b6ef8; color: #3b6ef8; }

.switch-row { display: flex; justify-content: space-between; align-items:flex-start;}
.switch-name { font-size: 0.88rem; font-weight: 600; color: #1a1d2e; }
.switch-desc { font-size: 0.78rem; color: #6b7280; margin-top: 4px; line-height: 1.4;}
.toggle { width: 38px; height: 22px; background: #d1d5db; border-radius: 99px; position: relative; cursor: pointer; transition: background 0.2s; flex-shrink: 0;}
.toggle.on { background: #3b6ef8; }
.toggle::after { content: ''; position: absolute; width: 16px; height: 16px; background: white; border-radius: 50%; top: 3px; left: 3px; transition: left 0.2s; box-shadow: 0 1px 2px rgba(0,0,0,0.1);}
.toggle.on::after { left: 19px; }

.hotzone-row { display: flex; justify-content: space-between; align-items: center; }
.hotzone-label { font-size: 0.88rem; color: #1a1d2e; font-weight:500;}
.hotzone-val { width: 60px; padding: 6px; border: 1px solid #e2e4ec; border-radius: 6px; font-size: 1rem; font-weight: 700; text-align: center; outline: none; }

.spec-select { width: 100%; padding: 10px 12px; border: 1px solid #e2e4ec; border-radius: 8px; font-size: 0.9rem; outline: none; background: white; appearance: none; }
.big-val { font-size: 2rem; font-weight: 800; color: #3b6ef8; line-height: 1; margin: 10px 0;}
.aa-badge { display: inline-block; background: #d1fae5; color: #059669; padding: 3px 10px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }

.size-input-wrap { display: flex; align-items: center; gap: 8px; }
.size-input-wide { flex: 1; padding: 10px 12px; border: 1px solid #e2e4ec; border-radius: 8px; font-size: 0.9rem; outline: none; box-sizing: border-box;}
.size-unit { font-size: 0.85rem; color: #6b7280; font-weight:500;}

/* 设计稿模式专属样式 */
.design-section { margin-bottom: 24px; }
.design-card { background: white; border: 1px solid #e8eaef; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);}
.design-card-title { display: flex; align-items: center; font-size: 1.05rem; font-weight: 700; color: #1a1d2e; margin-bottom: 6px; }
.design-card-hint { font-size: 0.85rem; color: #6b7280; margin-bottom: 20px; }
.url-input-wrap { display: flex; gap: 12px; margin-bottom: 14px; }
.url-input { flex: 1; padding: 10px 14px; border: 1px solid #e2e4ec; border-radius: 8px; font-size: 0.95rem; outline: none; background:#f9fafb;}
.url-input:focus { border-color: #3b6ef8; background:white;}
.url-input-actions { display: flex; justify-content: flex-end; gap: 10px; margin-bottom: 16px; }
.icon-btn { display: flex; align-items: center; gap: 6px; font-size: 0.85rem; color: #6b7280; padding: 6px 14px; border: 1px solid #e2e4ec; border-radius: 6px; background: white; cursor: pointer; }
.icon-btn:hover { border-color: #3b6ef8; color: #3b6ef8; background:#f0f4ff;}
.upload-area { border: 2px dashed #d1d5db; border-radius: 12px; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px 20px; background: #fafbfd; cursor: pointer; transition: all 0.2s; overflow: hidden;}
.upload-area:hover { border-color: #3b6ef8; background: #f0f4ff; }
.upload-icon { font-size: 36px; color: #9ca3af; margin-bottom: 10px;}
.upload-text { font-size: 0.95rem; color: #4b5563; font-weight:500;}
.upload-hint { font-size: 0.8rem; color: #9ca3af; margin-top: 6px;}
.upload-thumb { width: 100%; max-height: 260px; border-radius: 10px; object-fit: contain; box-shadow: 0 10px 24px rgba(15,23,42,0.4); margin-bottom: 14px; transition: transform 0.2s ease-out;}

.compare-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.cg-label { font-size: 0.85rem; font-weight: 600; color: #4b5563; margin-bottom: 10px; }
.slider-label-row { display: flex; justify-content: space-between; margin-bottom: 10px; }
.slider-hint { font-size: 0.8rem; color: #9ca3af; }
.slider-val { font-size: 0.9rem; font-weight: 700; color: #3b6ef8; }

.ai-item-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.ai-item-name { font-size: 0.95rem; font-weight: 600; color: #1a1d2e; }
.ai-item-desc { font-size: 0.82rem; color: #6b7280; }

.precision-tabs { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
.precision-opt { border: 2px solid #e2e4ec; border-radius: 12px; padding: 18px; cursor: pointer; display: flex; gap: 14px; transition: all 0.2s;}
.precision-opt.active { border-color: #3b6ef8; background: #f0f4ff; }
.precision-radio { width: 18px; height: 18px; border-radius: 50%; border: 2px solid #c8cad4; flex-shrink: 0; margin-top: 2px; }
.precision-opt.active .precision-radio { border-color: #3b6ef8; background: #3b6ef8; box-shadow: inset 0 0 0 3px white; }
.precision-opt-name { font-size: 0.95rem; font-weight: 700; color: #1a1d2e; margin-bottom: 4px;}
.precision-opt-desc { font-size: 0.8rem; color: #6b7280; }

.ignore-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.check-group-title { font-size: 0.9rem; font-weight: 700; color: #4b5563; margin-bottom: 12px; }
.checkbox-item { display: flex; align-items: center; gap: 8px; font-size: 0.88rem; color: #1a1d2e; margin-bottom: 10px; cursor: pointer;}
.checkbox-item input { width: 16px; height: 16px; accent-color: #3b6ef8;}

.anchor-grid { display: grid; grid-template-columns: repeat(3, 36px); grid-template-rows: repeat(3, 36px); gap: 6px; }
.anchor-dot { width: 36px; height: 36px; border: 2px solid #d1d5db; border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center; background:#fafbfd; transition: all 0.2s;}
.anchor-dot.active { background: #3b6ef8; border-color: #3b6ef8; }
.anchor-dot.active::after { content: ''; width: 8px; height: 8px; background: white; border-radius: 50%; }
</style>