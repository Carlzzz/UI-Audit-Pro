<template>
  <div class="page-container">
    <AppNavbar variant="simple" brand-text="返回首页" :show-user-dropdown="false" />
    <main class="profile-main">
      <h1 class="profile-page-title">个人信息设置</h1>

      <div class="form-row">
        <div class="field-label">账号名称</div>
        <div class="field-body">
          <input
            v-model.trim="accountName"
            class="field-input"
            type="text"
            maxlength="64"
            placeholder="登录与展示均使用此名称"
            autocomplete="username"
          />
        </div>
      </div>

      <div class="form-row form-row--top">
        <div class="field-label">头像</div>
        <div class="field-body field-body--avatar">
          <div class="avatar-preview">
            <div v-if="displayPhotoUrl" class="large-avatar large-avatar--img">
              <img :src="displayPhotoUrl" alt="" />
            </div>
            <div v-else class="large-avatar">{{ letterPreview }}</div>
          </div>
          <p class="hint">支持 JPG、PNG。选择图片后可缩放、拖动，再裁剪为圆形头像。</p>
          <input
            ref="fileInputRef"
            type="file"
            class="sr-only"
            accept="image/jpeg,image/png"
            @change="onPickFile"
          />
          <button type="button" class="btn-pick" @click="fileInputRef?.click()">选择图片并裁剪</button>
        </div>
      </div>

      <div class="form-row">
        <div class="field-label">原密码</div>
        <div class="field-body">
          <div class="pwd-wrap">
            <input
              class="field-input"
              :type="showP0 ? 'text' : 'password'"
              v-model="oldPassword"
              placeholder="修改密码时必填"
              autocomplete="current-password"
            />
            <span class="eye-icon" @click="showP0 = !showP0">{{ showP0 ? '👁️' : '🙈' }}</span>
          </div>
        </div>
      </div>
      <div class="form-row">
        <div class="field-label">新密码</div>
        <div class="field-body">
          <div class="pwd-wrap">
            <input
              class="field-input"
              :type="showP1 ? 'text' : 'password'"
              v-model="newPassword"
              placeholder="不少于 6 位"
              autocomplete="new-password"
            />
            <span class="eye-icon" @click="showP1 = !showP1">{{ showP1 ? '👁️' : '🙈' }}</span>
          </div>
        </div>
      </div>
      <div class="form-row">
        <div class="field-label">确认新密码</div>
        <div class="field-body">
          <div class="pwd-wrap">
            <input
              class="field-input"
              :type="showP2 ? 'text' : 'password'"
              v-model="confirmPassword"
              placeholder="再次输入新密码"
              autocomplete="new-password"
            />
            <span class="eye-icon" @click="showP2 = !showP2">{{ showP2 ? '👁️' : '🙈' }}</span>
          </div>
        </div>
      </div>
    </main>

    <div class="profile-footer-bar">
      <button type="button" class="btn-footer btn-footer--ghost" @click="onCancel">取消</button>
      <button type="button" class="btn-footer btn-footer--primary" @click="confirmAll">确认</button>
    </div>

    <Teleport to="body">
      <div v-if="cropOpen" class="crop-overlay" @click.self="closeCrop">
        <div class="crop-modal" role="dialog" aria-modal="true" aria-labelledby="crop-title">
          <div id="crop-title" class="crop-hd">裁剪头像</div>
          <div class="crop-body">
            <img v-show="cropSrc" ref="cropImgRef" :src="cropSrc" alt="" class="crop-target" />
          </div>
          <div class="crop-zoom-toolbar">
            <button type="button" class="zoom-btn" aria-label="缩小" @click="zoomCrop(-0.12)">−</button>
            <span class="zoom-hint">滚轮或按钮缩放，拖动图片调整区域</span>
            <button type="button" class="zoom-btn" aria-label="放大" @click="zoomCrop(0.12)">+</button>
          </div>
          <div class="crop-ft">
            <div class="crop-ft-inner">
              <button type="button" class="crop-btn crop-btn-cancel" @click="closeCrop">取消</button>
              <button type="button" class="crop-btn crop-btn-ok" @click="confirmCrop">确认</button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onUnmounted } from 'vue'
import Cropper from 'cropperjs'
import 'cropperjs/dist/cropper.css'
import { useRouter } from 'vue-router'
import AppNavbar from '../components/AppNavbar.vue'
import { useUserStore } from '../store/user'
import { showMsg } from '../utils/modal'
import axios from 'axios'
import { resolveAvatarDisplayUrl, isPhotoAvatar, letterAvatarText, API_ORIGIN } from '../utils/avatarUrl'

const router = useRouter()
const userStore = useUserStore()

const accountName = ref(String(userStore.userInfo?.username || '').trim())
const initialUsername = ref(accountName.value)

const fileInputRef = ref(null)
const cropSrc = ref('')
const cropOpen = ref(false)
const cropImgRef = ref(null)
let cropper = null

const showP0 = ref(false)
const showP1 = ref(false)
const showP2 = ref(false)
const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')

const cacheBust = ref(0)

const displayPhotoUrl = computed(() => {
  const a = userStore.userInfo?.avatar
  if (!a || !isPhotoAvatar(a)) return ''
  const u = resolveAvatarDisplayUrl(a)
  if (!u) return ''
  return cacheBust.value ? `${u}${u.includes('?') ? '&' : '?'}t=${cacheBust.value}` : u
})

const letterPreview = computed(() =>
  letterAvatarText(accountName.value || userStore.userInfo?.username, userStore.userInfo?.avatar)
)

function destroyCropper() {
  if (cropper) {
    cropper.destroy()
    cropper = null
  }
}

function zoomCrop(delta) {
  if (cropper) cropper.zoom(delta)
}

function closeCrop() {
  cropOpen.value = false
  destroyCropper()
  if (cropSrc.value) {
    URL.revokeObjectURL(cropSrc.value)
    cropSrc.value = ''
  }
}

async function onPickFile(e) {
  const f = e.target.files?.[0]
  if (e.target) e.target.value = ''
  if (!f) return
  if (!/^image\/(jpeg|png)$/i.test(f.type)) {
    showMsg('提示', '请上传 JPG 或 PNG 图片', 'warning')
    return
  }
  if (f.size > 8 * 1024 * 1024) {
    showMsg('提示', '图片需小于 8MB', 'warning')
    return
  }
  if (cropSrc.value) URL.revokeObjectURL(cropSrc.value)
  cropSrc.value = URL.createObjectURL(f)
  cropOpen.value = true
  await nextTick()
  destroyCropper()
  if (cropImgRef.value) {
    cropper = new Cropper(cropImgRef.value, {
      aspectRatio: 1,
      viewMode: 1,
      dragMode: 'move',
      autoCropArea: 0.88,
      responsive: true,
      background: false,
      zoomable: true,
      zoomOnTouch: true,
      zoomOnWheel: true,
      wheelZoomRatio: 0.12,
    })
  }
}

function confirmCrop() {
  if (!cropper || !userStore.userInfo?.id) return
  const canvas = cropper.getCroppedCanvas({
    width: 256,
    height: 256,
    imageSmoothingEnabled: true,
    imageSmoothingQuality: 'high',
  })
  canvas.toBlob(
    async (blob) => {
      if (!blob) {
        showMsg('失败', '无法生成图片', 'error')
        return
      }
      const fd = new FormData()
      fd.append('file', blob, 'avatar.jpg')
      fd.append('user_id', String(userStore.userInfo.id))
      try {
        const res = await axios.post(`${API_ORIGIN}/api/upload_avatar`, fd, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
        if (res.data.status === 'success') {
          userStore.updateAvatar(res.data.avatar_url)
          cacheBust.value = Date.now()
          closeCrop()
          await showMsg('保存成功', '头像图片已更新', 'success')
        } else {
          showMsg('保存失败', res.data.message || '请重试', 'error')
        }
      } catch (err) {
        console.error(err)
        const detail = err.response?.data?.detail
        showMsg('上传失败', typeof detail === 'string' ? detail : '请稍后重试', 'error')
      }
    },
    'image/jpeg',
    0.92
  )
}

function onCancel() {
  router.push('/')
}

async function confirmAll() {
  const uid = userStore.userInfo?.id
  if (!uid) return

  const name = accountName.value.trim()
  if (!name) {
    return showMsg('提示', '账号名称不能为空', 'warning')
  }

  const pwdAny = !!(oldPassword.value || newPassword.value || confirmPassword.value)
  if (pwdAny) {
    if (!oldPassword.value || !newPassword.value) {
      return showMsg('提示', '修改密码时请填写原密码与新密码', 'warning')
    }
    if (newPassword.value.length < 6) {
      return showMsg('提示', '新密码至少 6 位', 'warning')
    }
    if (newPassword.value !== confirmPassword.value) {
      return showMsg('提示', '两次输入的新密码不一致', 'warning')
    }
  }

  const nameChanged = name !== initialUsername.value

  if (!nameChanged && !pwdAny) {
    return showMsg('提示', '没有需要保存的修改', 'info')
  }

  try {
    if (nameChanged) {
      const res = await axios.post(`${API_ORIGIN}/api/update_profile`, {
        user_id: uid,
        username: name,
      })
      if (res.data.status !== 'success') {
        showMsg('保存失败', res.data.message || '请重试', 'error')
        return
      }
      userStore.updateUserInfo({ username: name })
      initialUsername.value = name
    }

    if (pwdAny) {
      const res = await axios.post(`${API_ORIGIN}/api/update_password`, {
        user_id: uid,
        old_password: oldPassword.value,
        new_password: newPassword.value,
      })
      if (res.data.status !== 'success') {
        showMsg('保存失败', res.data.message || '请重试', 'error')
        return
      }
      oldPassword.value = ''
      newPassword.value = ''
      confirmPassword.value = ''
    }

    await showMsg('保存成功', '个人信息已更新', 'success')
  } catch (e) {
    console.error(e)
    const detail = e.response?.data?.detail
    showMsg('保存失败', typeof detail === 'string' ? detail : '请稍后重试', 'error')
  }
}

onUnmounted(() => {
  closeCrop()
})
</script>

<style scoped>
.page-container {
  background: #f4f6fb;
  min-height: 100vh;
  box-sizing: border-box;
}

.profile-main {
  width: 100%;
  max-width: 920px;
  margin: 0 auto;
  padding: calc(var(--nav-height, 56px) + 32px) 32px 88px;
  box-sizing: border-box;
}

.profile-page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a1d2e;
  margin: 0 0 28px;
  text-align: left;
  letter-spacing: -0.02em;
}

.form-row {
  display: grid;
  grid-template-columns: minmax(100px, 140px) minmax(0, 1fr);
  column-gap: 28px;
  align-items: start;
  margin-bottom: 20px;
}

.form-row--top .field-label {
  padding-top: 6px;
  line-height: 1.4;
}

.field-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #374151;
  line-height: 44px;
  text-align: left;
}

.field-body {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
  width: 100%;
  max-width: 420px;
}

.field-body--avatar {
  max-width: 420px;
}

.field-input {
  width: 100%;
  height: 44px;
  padding: 0 12px;
  border: 1px solid #e2e4ec;
  border-radius: 8px;
  outline: none;
  box-sizing: border-box;
  font-size: 0.95rem;
}

.field-input:focus {
  border-color: #1a6aff;
}

.pwd-wrap {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
  max-width: 420px;
}

.pwd-wrap .field-input {
  padding-right: 40px;
}

.eye-icon {
  position: absolute;
  right: 10px;
  cursor: pointer;
  user-select: none;
  font-size: 14px;
  opacity: 0.75;
}

.avatar-preview {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 12px;
}

.large-avatar {
  width: 88px;
  height: 88px;
  background: #1a6aff;
  border-radius: 50%;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: bold;
}

.large-avatar--img {
  padding: 0;
  border: 2px solid #e8eaf0;
  overflow: hidden;
  background: #f3f4f6;
}

.large-avatar--img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hint {
  font-size: 0.82rem;
  color: #6b7280;
  line-height: 1.6;
  margin: 0 0 12px;
  text-align: left;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

.btn-pick {
  height: 40px;
  padding: 0 18px;
  border: 1px solid #e2e4ec;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  background: #fff;
  color: #374151;
  font-weight: 600;
}

.btn-pick:hover {
  background: #f9fafb;
  border-color: #c9cdd6;
}

.profile-footer-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  padding: 0 20px;
  background: rgba(255, 255, 255, 0.94);
  border-top: 1px solid #e8eaf0;
  z-index: 500;
  backdrop-filter: blur(8px);
  box-sizing: border-box;
}

.btn-footer {
  width: 100px;
  height: 40px;
  padding: 0;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  box-sizing: border-box;
  flex-shrink: 0;
}

.btn-footer--primary {
  border: none;
  background: #1a6aff;
  color: #fff;
}

.btn-footer--primary:hover {
  background: #1557e6;
}

.btn-footer--ghost {
  border: 1px solid #e2e4ec;
  background: #fff;
  color: #374151;
}

.btn-footer--ghost:hover {
  background: #f9fafb;
  border-color: #c9cdd6;
}

.crop-overlay { position: fixed; inset: 0; z-index: 10050; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; padding: 16px; }
.crop-modal { background: #fff; border-radius: 14px; max-width: 520px; width: 100%; box-shadow: 0 20px 50px rgba(0,0,0,0.2); overflow: hidden; }
.crop-hd { padding: 16px 18px; font-weight: 700; font-size: 1rem; color: #1a1d2e; border-bottom: 1px solid #e8eaf0; }
.crop-body { padding: 16px; max-height: min(70vh, 420px); }
.crop-target { display: block; max-width: 100%; max-height: 56vh; }
.crop-body :deep(.cropper-container) { max-height: 56vh; }
.crop-zoom-toolbar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 0 16px 10px;
}
.zoom-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: #fff;
  font-size: 1.35rem;
  line-height: 1;
  cursor: pointer;
  color: #374151;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.zoom-btn:hover { background: #f3f4f6; }
.zoom-hint { font-size: 0.76rem; color: #6b7280; text-align: center; line-height: 1.4; flex: 1; min-width: 0; }
.crop-ft {
  margin-top: 10px;
  padding: 14px 18px;
  border-top: 1px solid #e8eaf0;
  background: #fafbfc;
}
.crop-ft-inner { display: flex; gap: 10px; width: 100%; }
.crop-btn {
  flex: 1;
  min-width: 0;
  height: 40px;
  padding: 0 12px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
}
.crop-btn-cancel {
  border: 1px solid #e5e7eb;
  background: #fff;
  color: #374151;
}
.crop-btn-cancel:hover { background: #f9fafb; }
.crop-btn-ok {
  border: none;
  background: #1A6AFF;
  color: #fff;
}
.crop-btn-ok:hover { background: #1557e6; }
</style>
