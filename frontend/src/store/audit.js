import { defineStore } from 'pinia'

// 默认基准规范（全量4大类默认值）
const defaultBaseline = {
  colors: [{ hex: '#256af4', label: '主题色' }, { hex: '#2f54eb', label: '次要色' }],
  nearColorCheck: true, fontFamily: 'Inter, PingFang SC', lineHeights: '1.2, 1.5, 1.6',
  fontSizes: '32, 16, 14', spacingTokens: [4, 8, 16], gridTokens: [8], gridCheck: true,
  radiusTokens: [4, 8, 12], radiusCheck: true, shadowPreset: 'ant', iconStyleCheck: true,
  minClickArea: 44, hoverCheck: true, textOverflow: 'ellipsis', responsiveCheck: true,
  emptyStateCheck: true, loadingStateCheck: true, imageSizeLimit: 500, webpCheck: true,
  hardcodeCheck: true, deadlinkCheck: true, altCheck: true, domSemantics: true, focusOrder: true
}

const defaultDesign = {
  url: '', compareWidth: 1440, deviceType: 'desktop', colorThreshold: 10,
  aiAnalysis: true, aiSummary: true, precisionMode: 'pixel', ignoreStatus: true, ignoreAds: false, anchor: 0
}

export const useAuditStore = defineStore('audit', {
  state: () => ({
    targetUrl: '',
    checkMode: 'baseline',
    // 全局配置持久化
    globalConfig: JSON.parse(localStorage.getItem('globalConfig')) || {
      baseline: defaultBaseline,
      design: defaultDesign
    },
    // 单次走查的临时配置
    taskConfig: null,
    reportData: null
  }),
  actions: {
    setTargetUrl(url) { this.targetUrl = url },
    setCheckMode(mode) { this.checkMode = mode },
    saveGlobalConfig(configObj) {
      this.globalConfig = JSON.parse(JSON.stringify(configObj))
      localStorage.setItem('globalConfig', JSON.stringify(this.globalConfig))
    },
    setTaskConfig(configObj) {
      this.taskConfig = JSON.parse(JSON.stringify(configObj))
    },
    setReportData(data) { this.reportData = data }
  }
})