/**
 * 与 Report / Dashboard 共用的分类与紧急度规则。
 * 视觉一致性下「主题色 / 品牌色」类问题为高紧急度。
 */

const categoryMapping = {
  visual: ['视觉', '排版规范', '按钮规范', '表单规范', '导航规范', '展示规范', '间距规范', '像素级对比'],
  interaction: ['交互', '无障碍'],
  functional: ['布局', '系统报错', '功能障碍', '响应式', '死链', '空状态', '加载状态'],
  /** 文案与话术：全局用语风格、同类场景文案一致性、中英文空格、日期格式等（非资源体积类） */
  content: ['质量', '文案', '话术']
}

const THEME_COLOR_RE = /主题色|品牌色|主品牌色/

export function getCategoryType(category, issue) {
  const title = issue?.title != null ? String(issue.title) : ''
  if (title.includes('图片体积过大')) return 'functional'
  const cat = category ? String(category) : ''
  if (!cat) return 'visual'
  for (const [type, keywords] of Object.entries(categoryMapping)) {
    if (keywords.some((kw) => cat.includes(kw))) return type
  }
  return 'visual'
}

/** 视觉一致性维度内，主题色/品牌色相关为高 */
export function isVisualThemeColorHighUrgency(issue) {
  const text = `${issue?.title || ''}${issue?.desc || ''}${issue?.suggestion || ''}`
  if (!THEME_COLOR_RE.test(text)) return false
  return getCategoryType(issue?.category || '', issue) === 'visual'
}

export function getIssueUrgency(issue) {
  if (isVisualThemeColorHighUrgency(issue)) return 'high'
  const type = getCategoryType(issue?.category || '', issue)
  if (type === 'functional') return 'high'
  if (type === 'interaction') return 'high'
  if (type === 'visual') return 'medium'
  return 'low'
}
