<template>
    <div class="page-container">
      <AppNavbar variant="simple" brand-text="返回首页" :show-user-dropdown="false" />
      <div class="setting-card">
        <h2 style="margin-bottom:24px; color:#1a1d2e;">个人信息设置</h2>
        
        <div class="avatar-preview">
          <div class="large-avatar">{{ newAvatar || '?' }}</div>
        </div>
  
        <div class="input-group">
          <label>当前账号</label>
          <input type="text" :value="userStore.userInfo?.username" disabled style="background:#f9fafb; color:#9ca3af;">
        </div>
        
        <div class="input-group">
          <label>自定义头像 (建议输入1-2个字符或Emoji)</label>
          <input type="text" v-model="newAvatar" maxlength="2" placeholder="如: PM, 🐶">
        </div>
  
        <button class="btn-primary" @click="saveProfile">保存修改</button>
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
  const newAvatar = ref(userStore.userInfo?.avatar || '')
  
  const saveProfile = async () => {
    try {
      const res = await axios.post('http://localhost:8000/api/update_avatar', {
        user_id: userStore.userInfo.id,
        avatar: newAvatar.value
      })
      if (res.data.status === 'success') {
        userStore.updateAvatar(newAvatar.value)
        await showMsg('保存成功', '头像已更新！', 'success')
        router.push('/')
      } else {
        showMsg('保存失败', res.data.message, 'error')
      }
    } catch (e) {
      console.error(e)
      showMsg('保存失败', '网络请求错误，请确保 Python 后端已重启并运行在 8000 端口', 'error')
    }
  }
  </script>
  
  <style scoped>
  .page-container { background: #f4f6fb; min-height: 100vh; padding-top: 100px; display: flex; justify-content: center; }
  .setting-card { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); width: 450px; }
  .avatar-preview { display: flex; justify-content: center; margin-bottom: 30px; }
  .large-avatar { width: 80px; height: 80px; background: #1A6AFF; border-radius: 50%; color: white; display: flex; align-items: center; justify-content: center; font-size: 28px; font-weight: bold; }
  .input-group { margin-bottom: 20px; }
  .input-group label { display: block; font-size: 0.85rem; color: #4b5563; margin-bottom: 8px; font-weight: 600;}
  .input-group input { width: 100%; padding: 12px; border: 1px solid #e2e4ec; border-radius: 8px; outline: none; box-sizing: border-box; }
  .input-group input:focus { border-color: #1A6AFF; }
  .btn-primary { width: 100%; padding: 12px; border: none; border-radius: 8px; font-size: 1rem; cursor: pointer; background: #1A6AFF; color: white; margin-top: 10px; font-weight: 600;}
  </style>