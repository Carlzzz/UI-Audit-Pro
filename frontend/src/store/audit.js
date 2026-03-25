import { defineStore } from 'pinia'

/** 刷新 /report 时从 sessionStorage 恢复最近一次走查结果（仅存内存会话，关闭标签页后清除） */
export const REPORT_SNAPSHOT_KEY = 'ui_audit_report_snapshot'

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
      try {
        if (data && typeof data === 'object') {
          sessionStorage.setItem(REPORT_SNAPSHOT_KEY, JSON.stringify(data))
        } else {
          sessionStorage.removeItem(REPORT_SNAPSHOT_KEY)
        }
      } catch (e) {
        console.warn('[audit] 报告快照写入 sessionStorage 失败', e)
      }
    },
    /** 从 session 恢复最近一次报告（用于 /report 刷新后仍可读） */
    restoreReportFromSession() {
      try {
        const raw = sessionStorage.getItem(REPORT_SNAPSHOT_KEY)
        if (!raw) return false
        const data = JSON.parse(raw)
        if (data && typeof data === 'object') {
          this.reportData = data
          return true
        }
      } catch (e) {
        console.warn('[audit] 报告快照读取失败', e)
      }
      return false
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
