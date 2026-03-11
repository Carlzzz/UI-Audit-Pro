<template>
  <div class="page-container">
    <AppNavbar variant="simple" brand-text="返回首页" :show-user-dropdown="false" />
    <div class="setting-card">
      <h2 style="margin-bottom:24px; color:#1a1d2e;">修改密码</h2>

      <div class="input-group">
        <label>原密码</label>
        <div class="pwd-wrap">
          <input :type="showP1 ? 'text' : 'password'" v-model="oldPassword" placeholder="请输入当前密码">
          <span class="eye-icon" @click="showP1 = !showP1">{{ showP1 ? '👁️' : '🙈' }}</span>
        </div>
      </div>
      <div class="input-group">
        <label>新密码</label>
        <div class="pwd-wrap">
          <input :type="showP2 ? 'text' : 'password'" v-model="newPassword" placeholder="请输入新密码">
          <span class="eye-icon" @click="showP2 = !showP2">{{ showP2 ? '👁️' : '🙈' }}</span>
        </div>
      </div>
      <div class="input-group">
        <label>确认新密码</label>
        <div class="pwd-wrap">
          <input :type="showP3 ? 'text' : 'password'" v-model="confirmPassword" placeholder="请再次输入新密码">
          <span class="eye-icon" @click="showP3 = !showP3">{{ showP3 ? '👁️' : '🙈' }}</span>
        </div>
      </div>

      <button class="btn-primary" @click="savePassword">保存修改并重新登录</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AppNavbar from '../components/AppNavbar.vue'
import { useUserStore } from '../store/user'
import { showMsg } from '../utils/modal'
import axios from 'axios'

const router = useRouter()
const userStore = useUserStore()

const showP1 = ref(false)
const showP2 = ref(false)
const showP3 = ref(false)

const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')

const savePassword = async () => {
  if (!oldPassword.value || !newPassword.value) return showMsg('提示', '请填写完整', 'warning')
  if (newPassword.value !== confirmPassword.value) return showMsg('提示', '两次输入的新密码不一致', 'warning')

  try {
    const res = await axios.post('http://localhost:8000/api/update_password', {
      user_id: userStore.userInfo.id,
      old_password: oldPassword.value,
      new_password: newPassword.value
    })
    
    if (res.data.status === 'success') {
      await showMsg('修改成功', '密码修改成功，请使用新密码重新登录！', 'success')
      userStore.logout()
      router.push('/login')
    } else {
      showMsg('修改失败', res.data.message, 'error')
    }
  } catch (e) {
    showMsg('系统错误', '网络请求错误，请确保后端服务已重启', 'error')
  }
}
</script>

<style scoped>
.page-container { background: #f4f6fb; min-height: 100vh; padding-top: 100px; display: flex; justify-content: center; }
.setting-card { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); width: 450px; }
.input-group { margin-bottom: 20px; }
.input-group label { display: block; font-size: 0.85rem; color: #4b5563; margin-bottom: 8px; font-weight: 600;}
.pwd-wrap { position: relative; display: flex; align-items: center;}
.pwd-wrap input { width: 100%; padding: 12px 40px 12px 12px; border: 1px solid #e2e4ec; border-radius: 8px; outline: none; box-sizing: border-box; font-family: inherit;}
.pwd-wrap input:focus { border-color: #3b6ef8; }
.eye-icon { position: absolute; right: 12px; cursor: pointer; opacity: 0.6; transition: opacity 0.2s;}
.eye-icon:hover { opacity: 1; }
.btn-primary { width: 100%; padding: 12px; border: none; border-radius: 8px; font-size: 1rem; cursor: pointer; background: #3b6ef8; color: white; margin-top: 10px; font-weight: 600;}
</style>