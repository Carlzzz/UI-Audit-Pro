import { defineStore } from 'pinia'

export const useAuditStore = defineStore('audit', {
  state: () => ({
    checkMode: 'baseline',
    targetUrl: '',
    reportData: null,
    globalConfig: {
      baseline: null,
      design: null,
      component: null
    },
    taskConfig: null
  }),
  actions: {
    setCheckMode(mode) {
      this.checkMode = mode
    },
    setTargetUrl(url) {
      this.targetUrl = url
    },
    setReportData(data) {
      this.reportData = data
    },
    setTaskConfig(config) {
      this.taskConfig = config
    },
    setGlobalConfig(mode, config) {
      this.globalConfig[mode] = config
    }
  }
})
