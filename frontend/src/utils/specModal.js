import { showToastInfo } from './modal'
import { normalizeAsciiPunctuation } from './punctuationNormalize'

/**
 * 规范标签去重：8px / 8 / 8.0px 视为相同；14*14px 与 14 * 14px 视为相同
 * @param {unknown} val
 */
export function normalizeSpecValueForDedup(val) {
  const s = String(val).trim().toLowerCase()
  if (!s) return ''
  if (/\d+\s*\*\s*\d+/.test(s)) {
    return s.replace(/\s/g, '')
  }
  const px = s.match(/^([\d.]+)\s*px$/i)
  if (px) return `${parseFloat(px[1])}px`
  const num = s.match(/^([\d.]+)$/)
  if (num) return `${parseFloat(num[1])}px`
  return s
}

/**
 * 计算浮层位置（贴触发元素，不超出视口）
 * @param {import('vue').Reactive} panel 需含 left、top
 */
export function applyFloatPanelPosition(panel, e, panelW = 328, panelH = 240) {
  const r = e?.currentTarget?.getBoundingClientRect?.() || { left: 80, top: 100, bottom: 140, width: 48 }
  let left = r.left
  let top = r.bottom + 8
  if (left + panelW > window.innerWidth - 8) left = Math.max(8, window.innerWidth - panelW - 8)
  else left = Math.max(8, left)
  if (top + panelH > window.innerHeight) {
    top = Math.max(8, r.top - panelH - 8)
  }
  panel.left = left
  panel.top = top
}

/**
 * 在触发元素附近打开无蒙层小弹窗（由 SpecAddFloat 组件承载）
 * @param {import('vue').Reactive} specFloat 含 open,left,top,title,fieldLabel,defaultVal,mode,arr
 */
export function openSpecAddPanel(specFloat, e, arr, defaultVal, title) {
  const d = String(defaultVal ?? '').trim()
  let mode = 'plain'
  if (d.includes('*')) mode = 'xy'
  else if (/px$/i.test(d)) mode = 'px'
  else mode = 'plain'

  specFloat.arr = arr
  specFloat.defaultVal = d
  specFloat.title = title || '添加规范值'
  specFloat.fieldLabel = (title || '').replace(/^添加/, '').trim() || '规范值'
  specFloat.mode = mode

  applyFloatPanelPosition(specFloat, e, 328, 220)
  specFloat.open = true
}

/**
 * 全局色盘：添加/修改色值浮层（与 SpecAddFloat 栅格添加同定位逻辑，无蒙层）
 */
export function openColorEditPanel(colorFloat, e, label, hex, title = '修改色值') {
  colorFloat.title = title
  colorFloat.label = label
  colorFloat.hex = hex
  applyFloatPanelPosition(colorFloat, e, 340, 300)
  colorFloat.open = true
}

export function confirmSpecAddPanel(specFloat, val) {
  if (!specFloat.arr || !val) {
    specFloat.open = false
    return
  }
  const next = normalizeAsciiPunctuation(String(val)).trim()
  if (!next) {
    specFloat.open = false
    return
  }
  const norm = normalizeSpecValueForDedup(next)
  const dup = specFloat.arr.some((existing) => normalizeSpecValueForDedup(existing) === norm)
  if (dup) {
    showToastInfo('已存在相同的规范值')
    specFloat.open = false
    return
  }
  specFloat.arr.push(val)
  specFloat.open = false
}
