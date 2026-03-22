/**
 * 与 Report / Dashboard 共用的分类与紧急度规则。
 * 视觉一致性下「主题色 / 品牌色」类问题为高紧急度。
 */

const categoryMapping = {
  visual: ['视觉', '排版规范', '按钮规范', '表单规范', '导航规范', '展示规范', '间距规范'],
  interaction: ['交互', '布局', '无障碍', '系统报错'],
  content: ['质量', '性能与质量', '文案', '话术']
}

const THEME_COLOR_RE = /主题色|品牌色|主品牌色/

export function getCategoryType(category) {
  if (!category) return 'visual'
  for (const [type, keywords] of Object.entries(categoryMapping)) {
    if (keywords.some((kw) => category.includes(kw))) return type
  }
  return 'visual'
}

/** 视觉一致性维度内，主题色/品牌色相关为高 */
export function isVisualThemeColorHighUrgency(issue) {
  const text = `${issue?.title || ''}${issue?.desc || ''}${issue?.suggestion || ''}`
  if (!THEME_COLOR_RE.test(text)) return false
  return getCategoryType(issue?.category || '') === 'visual'
}

export function getIssueUrgency(issue) {
  if (isVisualThemeColorHighUrgency(issue)) return 'high'
  const type = getCategoryType(issue?.category || '')
  if (type === 'interaction') return 'high'
  if (type === 'visual') return 'medium'
  return 'low'
}
