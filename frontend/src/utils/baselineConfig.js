/**
 * 将旧版字符串或异常数据规范为断点数组（如 ['768px','1024px']），与栅格 tag 一致。
 * @param {Record<string, unknown>} cfg baseline_config 片段（会就地修改）
 */
export function normalizeResponsiveBreakpoints(cfg) {
  if (!cfg || typeof cfg !== 'object') return
  const fallback = ['768px', '1024px', '1440px']
  const toPx = (x) => {
    const s = String(x).trim()
    if (!s) return null
    return /px$/i.test(s) ? s : `${s.replace(/px$/i, '')}px`
  }
  const raw = cfg.responsiveBreakpoints
  if (Array.isArray(raw)) {
    const arr = raw.map(toPx).filter(Boolean)
    cfg.responsiveBreakpoints = arr.length ? arr : [...fallback]
    return
  }
  if (typeof raw === 'string' && raw.trim()) {
    cfg.responsiveBreakpoints = raw.split(',').map(toPx).filter(Boolean)
    if (cfg.responsiveBreakpoints.length === 0) cfg.responsiveBreakpoints = [...fallback]
  } else {
    cfg.responsiveBreakpoints = [...fallback]
  }
}
