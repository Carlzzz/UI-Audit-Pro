/**
 * 报告页展示：将 CSS cursor 等技术英文转为中文（兼容历史数据）
 */
const CURSOR_EN_TO_ZH = {
  auto: '自动',
  default: '默认',
  pointer: '手型指针',
  text: '文本选择',
  move: '移动',
  'not-allowed': '禁止',
  wait: '等待',
  help: '帮助',
  progress: '处理中',
  crosshair: '十字准星',
  grab: '抓取',
  grabbing: '抓取中',
  none: '无',
  'col-resize': '列宽调整',
  'row-resize': '行高调整',
  'n-resize': '纵向调整',
  'e-resize': '横向调整',
  'nwse-resize': '对角调整',
  'ns-resize': '纵向调整',
  'ew-resize': '横向调整',
  alias: '快捷方式',
  cell: '单元格选择',
  copy: '复制',
  zoomin: '放大',
  zoomout: '缩小',
}

/**
 * @param {string} text
 * @returns {string}
 */
export function localizeCursorTermsInText(text) {
  if (text == null || typeof text !== 'string') return text
  let t = text
  const sortedKeys = Object.keys(CURSOR_EN_TO_ZH).sort((a, b) => b.length - a.length)
  for (const en of sortedKeys) {
    const zh = CURSOR_EN_TO_ZH[en]
    const esc = en.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    t = t.replace(new RegExp(`\\b${esc}\\b`, 'gi'), zh)
  }
  return t
}
