import Swal from 'sweetalert2'

// 统一定制基础样式 (融入系统的品牌蓝)
const customSwal = Swal.mixin({
  confirmButtonColor: '#3b6ef8',
  cancelButtonColor: '#f3f4f6',
  allowOutsideClick: false // 🌟 核心设置：禁止点击空白处消失，必须强制确认
})

// 1. 普通提示弹窗 (成功/错误/警告)
export const showMsg = (title, text = '', icon = 'info') => {
  return customSwal.fire({
    title,
    text,
    icon,
    confirmButtonText: '我知道了'
  })
}

// 2. 确认/取消弹窗
export const showConfirm = (title, text = '') => {
  return customSwal.fire({
    title,
    text,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: '确定',
    cancelButtonText: '<span style="color:#4b5563">取消</span>'
  }).then(res => res.isConfirmed)
}

// 3. 文本输入弹窗
export const showPrompt = (title, inputPlaceholder = '') => {
  return customSwal.fire({
    title,
    input: 'text',
    inputPlaceholder,
    showCancelButton: true,
    confirmButtonText: '确定',
    cancelButtonText: '<span style="color:#4b5563">取消</span>'
  }).then(res => res.isConfirmed ? res.value : null)
}