/**
 * 将中文输入法常见的全角标点转为半角 ASCII，便于逗号分隔、数值解析与后端规则一致。
 * 用于规范输入、列表类字段失焦时。
 */
export function normalizeAsciiPunctuation(input) {
  if (input == null || input === '') return ''
  let s = String(input)
  s = s.replace(/\uFF0C/g, ',') // ，
  s = s.replace(/\u3001/g, ',') // 、
  s = s.replace(/\uFF1B/g, ';') // ；
  s = s.replace(/\uFF1A/g, ':') // ：
  s = s.replace(/\uFF08/g, '(') // （
  s = s.replace(/\uFF09/g, ')') // ）
  s = s.replace(/\u3010/g, '[') // 【
  s = s.replace(/\u3011/g, ']') // 】
  s = s.replace(/\u201C|\u201D/g, '"') // “ ”
  s = s.replace(/\u2018|\u2019/g, "'") // ‘ ’
  return s
}

/**
 * 逗号分隔内容在规范化后统一为「逗号 + 空格」，便于阅读（字体大小、行高、字重、过渡时间、字体族列表等）
 */
export function formatCommaListSpacing(input) {
  if (input == null || input === '') return ''
  let s = normalizeAsciiPunctuation(String(input))
  const parts = s.split(/[,，]/).map((p) => p.trim()).filter((p) => p.length > 0)
  return parts.join(', ')
}
