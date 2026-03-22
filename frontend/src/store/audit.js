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
    taskConfig: null,
    /** 新建走查页「保存」写入的会话快照（不写规则管理 API）；开启走查优先使用，编辑表单后会自动失效 */
    sessionDraft: {
      baseline: null,
      component: null,
      design: null
    }
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
      if (config == null) {
        this.taskConfig = null
        return
      }
      try {
        this.taskConfig = JSON.parse(JSON.stringify(config))
      } catch {
        this.taskConfig = null
      }
    },
    setGlobalConfig(mode, config) {
      this.globalConfig[mode] = config
    },
    /** 将当前模式配置快照存入内存，供本次「开启走查」使用 */
    setSessionDraft(mode, config) {
      if (!['baseline', 'component', 'design'].includes(mode)) return
      try {
        this.sessionDraft[mode] = config == null ? null : JSON.parse(JSON.stringify(config))
      } catch {
        this.sessionDraft[mode] = null
      }
    },
    clearSessionDraft(mode) {
      if (mode && ['baseline', 'component', 'design'].includes(mode)) {
        this.sessionDraft[mode] = null
      } else {
        this.sessionDraft.baseline = null
        this.sessionDraft.component = null
        this.sessionDraft.design = null
      }
    }
  }
})
