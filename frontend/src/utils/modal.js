import SwalBase from 'sweetalert2'
import 'sweetalert2/dist/sweetalert2.min.css'

/**
 * 带统一样式的 Swal（见 main.css .ui-audit-swal）。
 * Swal.mixin() 返回新类，需用此导出替代各处 `import Swal from 'sweetalert2'`。
 */
export const Swal = SwalBase.mixin({
  customClass: {
    popup: 'ui-audit-swal',
    confirmButton: 'ui-audit-swal-confirm',
    cancelButton: 'ui-audit-swal-cancel'
  },
  confirmButtonColor: '#1A6AFF',
  cancelButtonColor: '#f3f4f6',
  allowOutsideClick: false
})

// 1. 普通提示弹窗 (成功/错误/警告)
export const showMsg = (title, text = '', icon = 'info') => {
  return Swal.fire({
    title,
    text,
    icon,
    confirmButtonText: '我知道了'
  })
}

/** 16×16 面状警告：圆填充 #FF931D，感叹号为白色 */
const CONFIRM_WARNING_ICON_SVG = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><circle cx="8" cy="8" r="8" fill="#FF931D"/><rect x="7.25" y="4" width="1.5" height="5" rx="0.75" fill="#fff"/><circle cx="8" cy="11.5" r="1" fill="#fff"/></svg>`

// 2. 确认/取消弹窗
export const showConfirm = (title, text = '') => {
  return Swal.fire({
    title,
    text,
    icon: 'warning',
    iconHtml: CONFIRM_WARNING_ICON_SVG,
    showCancelButton: true,
    confirmButtonText: '确定',
    cancelButtonText: '<span style="color:#4b5563">取消</span>'
  }).then((res) => res.isConfirmed)
}

// 3. 文本输入弹窗
export const showPrompt = (title, inputPlaceholder = '') => {
  return Swal.fire({
    title,
    input: 'text',
    inputPlaceholder,
    showCancelButton: true,
    confirmButtonText: '确定',
    cancelButtonText: '<span style="color:#4b5563">取消</span>'
  }).then((res) => (res.isConfirmed ? res.value : null))
}

/** 20×20 面状成功图标：圆填充 #10C038，对勾为白色 */
const TOAST_SUCCESS_ICON_SVG = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="10" cy="10" r="10" fill="#10C038"/><path d="M5.5 10.2l2.5 2.5 5-3.5" stroke="#fff" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>`

/**
 * 顶部居中成功轻提示：无蒙版、单行 icon + 文案（样式见 main.css .ui-audit-toast--success）
 * @param {string} title
 * @param {number} [timer=1500] ms
 */
export const showToastSuccess = (title, timer = 1500) => {
  return Swal.fire({
    toast: true,
    position: 'top',
    icon: 'success',
    iconHtml: TOAST_SUCCESS_ICON_SVG,
    title,
    showConfirmButton: false,
    timer,
    timerProgressBar: false,
    customClass: {
      popup: 'ui-audit-toast ui-audit-toast--success'
    }
  })
}

/** 顶部轻提示（信息），用于重复值等提示 */
export const showToastInfo = (title, timer = 2000) => {
  return Swal.fire({
    toast: true,
    position: 'top',
    icon: 'info',
    title,
    showConfirmButton: false,
    timer
  })
}
