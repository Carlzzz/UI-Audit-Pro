<template>
    <div class="login-wrapper">
      <div class="login-card">
        <div class="logo-box">✦</div>
        <h2>自动化走查平台</h2>
        
        <div class="auth-tabs">
          <div class="auth-tab" :class="{ active: isLogin }" @click="isLogin = true">登录</div>
          <div class="auth-tab" :class="{ active: !isLogin }" @click="isLogin = false">注册</div>
        </div>
        
        <div class="input-group">
          <label>用户名</label>
          <input type="text" v-model="username" placeholder="请输入用户名">
        </div>
        <div class="input-group">
          <label>密码</label>
          <input type="password" v-model="password" placeholder="请输入密码" @keyup.enter="handleSubmit">
        </div>
        <div class="input-group" v-if="!isLogin">
          <label>确认密码</label>
          <input type="password" v-model="confirmPassword" placeholder="请再次输入密码" @keyup.enter="handleSubmit">
        </div>
        
        <button class="btn-primary login-btn" @click="handleSubmit">{{ isLogin ? '登录进入系统' : '注册并登录' }}</button>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useUserStore } from '../store/user'
  import { showMsg } from '../utils/modal'
  import axios from 'axios'
  
  const router = useRouter()
  const userStore = useUserStore()
  const isLogin = ref(true)
  
  const username = ref('')
  const password = ref('')
  const confirmPassword = ref('')
  
  const handleSubmit = async () => {
    if (!username.value || !password.value) return showMsg('提示', '请填写完整信息', 'warning')
    
    if (isLogin.value) {
      try {
        const res = await axios.post('http://localhost:8000/api/login', { username: username.value, password: password.value })
        if (res.data.status === 'success') {
          userStore.login(res.data.data)
          // 取消登录成功的弹窗，以免阻塞自动化走查
          router.push('/')
        }
      } catch (err) {
        showMsg('登录失败', '账号或密码错误', 'error')
      }
    } else {
      if (password.value !== confirmPassword.value) return showMsg('提示', '两次密码不一致', 'warning')
      try {
        const res = await axios.post('http://localhost:8000/api/register', { username: username.value, password: password.value })
        if (res.data.status === 'success') {
          // 同样取消注册成功的弹窗阻塞
          const loginRes = await axios.post('http://localhost:8000/api/login', { username: username.value, password: password.value })
          userStore.login(loginRes.data.data)
          router.push('/')
        } else {
          showMsg('注册失败', res.data.message, 'error')
        }
      } catch (err) {
        showMsg('系统错误', '注册请求失败，请稍后再试', 'error')
      }
    }
  }
  </script>
  
  <style scoped>
  .login-wrapper { height: 100vh; display: flex; align-items: center; justify-content: center; background: #f4f6fb; }
  .login-card { background: white; padding: 40px; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.08); width: 400px; text-align: center; }
  .logo-box { width: 48px; height: 48px; background: #3b6ef8; color: white; display: flex; align-items: center; justify-content: center; border-radius: 12px; font-size: 24px; margin: 0 auto 16px; }
  h2 { color: #1a1d2e; margin-bottom: 24px; font-size: 1.4rem;}
  
  .auth-tabs { display: flex; margin-bottom: 24px; border-bottom: 1px solid #e5e7eb; }
  .auth-tab { flex: 1; padding: 10px; cursor: pointer; color: #6b7280; font-size: 0.95rem; font-weight: 500; border-bottom: 2px solid transparent; transition: all 0.2s;}
  .auth-tab.active { color: #3b6ef8; border-bottom-color: #3b6ef8; font-weight: 700; }
  
  .input-group { text-align: left; margin-bottom: 18px; }
  .input-group label { display: block; font-size: 0.8rem; color: #4b5563; margin-bottom: 8px; font-weight: 600;}
  .input-group input { width: 100%; padding: 12px; border: 1px solid #e2e4ec; border-radius: 8px; outline: none; box-sizing: border-box; font-size: 0.95rem;}
  .input-group input:focus { border-color: #3b6ef8; }
  .login-btn { width: 100%; padding: 14px; border: none; border-radius: 8px; font-size: 1rem; cursor: pointer; background: #3b6ef8; color: white; margin-top: 10px; font-weight: bold;}
  .login-btn:hover { background: #256af4; }
  </style>