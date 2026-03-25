/** 将 AI 返回的 **关键词** 转为安全 HTML（先转义再替换） */

export function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

export function diagnosisMarkdownBoldToHtml(raw) {
  if (raw == null || typeof raw !== 'string') return ''
  const t = raw.trim()
  if (!t) return ''
  const escaped = escapeHtml(t)
  return escaped.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
}

/** 拆成多条（换行 / 句号），去掉行首 •- */
export function splitDiagnosisLines(raw) {
  if (!raw || typeof raw !== 'string') return []
  let t = raw.trim()
  if (!t) return []
  let parts = t.split(/\n+/).map((s) => s.trim()).filter(Boolean)
  if (parts.length === 1) {
    parts = parts[0].split(/[。！？]+/).map((s) => s.trim()).filter(Boolean)
  }
  return parts.map((line) => line.replace(/^[•\-\*]\s*/, '').trim()).filter(Boolean)
}
