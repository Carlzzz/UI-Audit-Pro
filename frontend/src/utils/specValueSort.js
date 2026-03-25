/**
 * 规范管理 / 走查配置：逗号分隔的纯数字列表按数值升序（字体大小、行高倍数、字重等）
 */
export function sortCommaSeparatedNumericList(str) {
  if (str == null || str === '') return str
  const raw = String(str)
  const parts = raw.split(/[,，]/).map((s) => s.trim()).filter(Boolean)
  if (parts.length <= 1) return raw
  const nums = parts.map((p) => ({ raw: p, n: parseFloat(p) }))
  if (nums.some((x) => Number.isNaN(x.n))) return raw
  nums.sort((a, b) => a.n - b.n)
  return nums.map((x) => x.raw).join(', ')
}

/**
 * 过渡时间：补齐单个 s、去掉重复 s、300ms 转为秒，再交给 sortCommaSeparatedDurations 排序
 */
export function normalizeTransitionDurationsList(str) {
  if (str == null || str === '') return ''
  const parts = String(str)
    .split(/[,，]/)
    .map((s) => s.trim())
    .filter(Boolean)
  if (parts.length === 0) return ''
  const norm = parts.map((p) => normalizeOneDurationToken(p)).filter(Boolean)
  return sortCommaSeparatedDurations(norm.join(', '))
}

function stripNumStr(n) {
  if (!Number.isFinite(n)) return ''
  const s = n.toFixed(6).replace(/\.?0+$/, '')
  return s || '0'
}

function normalizeOneDurationToken(tok) {
  let t = String(tok).trim().replace(/\s+/g, '')
  if (!t) return ''
  const ms = t.match(/^([\d.]+)\s*ms$/i)
  if (ms) {
    const sec = parseFloat(ms[1]) / 1000
    if (!Number.isFinite(sec)) return tok
    return `${stripNumStr(sec)}s`
  }
  t = t.replace(/s+$/gi, '')
  const num = t.match(/^([\d.]+)/)
  if (!num) return tok
  const v = parseFloat(num[1])
  if (!Number.isFinite(v)) return tok
  return `${stripNumStr(v)}s`
}

/**
 * 过渡时间：0.2s、0.25s、300ms 等按时长升序
 */
export function sortCommaSeparatedDurations(str) {
  if (str == null || str === '') return str
  const raw = String(str)
  const parts = raw.split(/[,，]/).map((s) => s.trim()).filter(Boolean)
  if (parts.length <= 1) return raw
  const parsed = parts.map((s) => {
    const m = s.match(/^([\d.]+)\s*(s|ms)?$/i)
    if (!m) return { s, sec: NaN }
    const v = parseFloat(m[1])
    const unit = (m[2] || 's').toLowerCase()
    const sec = unit === 'ms' ? v / 1000 : v
    return { s, sec }
  })
  if (parsed.some((p) => Number.isNaN(p.sec))) return raw
  parsed.sort((a, b) => a.sec - b.sec)
  return parsed.map((p) => p.s).join(', ')
}

function tokenSortKey(s) {
  const str = String(s).trim().toLowerCase()
  const star = str.match(/^(\d+(?:\.\d+)?)\s*\*\s*(\d+(?:\.\d+)?)\s*px$/i)
  if (star) return parseFloat(star[1]) * parseFloat(star[2])
  const px = str.match(/^(\d+(?:\.\d+)?)\s*px$/i)
  if (px) return parseFloat(px[1])
  const plain = str.match(/^(\d+(?:\.\d+)?)$/)
  if (plain) return parseFloat(plain[1])
  return 0
}

/**
 * 就地排序：4px、8px、14*14px 等标签按数值/面积升序
 */
export function sortPixelLikeTokenArray(arr) {
  if (!Array.isArray(arr) || arr.length <= 1) return
  const sorted = [...arr].sort((a, b) => tokenSortKey(a) - tokenSortKey(b))
  arr.splice(0, arr.length, ...sorted)
}
