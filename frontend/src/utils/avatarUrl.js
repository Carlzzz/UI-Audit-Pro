/** 与后端静态资源、登录态头像字段一致 */
export const API_ORIGIN = 'http://localhost:8000'

export function isPhotoAvatar(avatar) {
  if (!avatar || typeof avatar !== 'string') return false
  return avatar.startsWith('/uploads/') || avatar.startsWith('http') || avatar.startsWith('data:')
}

export function resolveAvatarDisplayUrl(avatar) {
  if (!avatar || typeof avatar !== 'string') return ''
  if (avatar.startsWith('/uploads/')) return `${API_ORIGIN}${avatar}`
  if (avatar.startsWith('http') || avatar.startsWith('data:')) return avatar
  return ''
}

/** 非图片头像时展示头像字段 1～2 字；图片地址或无字段时用用户名前两位 */
export function letterAvatarText(username, avatar) {
  const a = avatar
  if (a && typeof a === 'string' && !isPhotoAvatar(a)) return a.slice(0, 2)
  if (username) return String(username).slice(0, 2)
  return '?'
}
