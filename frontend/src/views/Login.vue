<template>
  <div class="login-wrapper">
    <!-- 底部水流涌动特效 + 装饰小 icon -->
    <div class="login-water-effect" aria-hidden="true">
      <svg width="0" height="0" style="position:absolute;overflow:hidden" aria-hidden="true">
        <defs>
          <linearGradient id="water-icon-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#6366f1"/>
            <stop offset="100%" stop-color="#1A6AFF"/>
          </linearGradient>
        </defs>
      </svg>
      <div class="wave wave-1"></div>
      <div class="wave wave-2"></div>
      <div class="wave wave-3"></div>
      <span class="water-icon water-icon-1"><IconStroke name="sparkle" size="sm" /></span>
      <span class="water-icon water-icon-2"><IconStroke name="palette" size="sm" /></span>
      <span class="water-icon water-icon-3"><IconStroke name="check" size="sm" /></span>
      <span class="water-icon water-icon-4"><IconStroke name="bolt" size="sm" /></span>
    </div>

    <a href="#" class="login-logo" @click.prevent="goTo('/')">
      <div class="login-logo-icon" aria-hidden="true">
        <IconStroke name="sparkle" size="md" class="logo-mark" />
      </div>
      <span class="login-logo-text">自动化走查平台</span>
    </a>

    <div class="login-main">
      <!-- 左侧：产品介绍卡片 -->
      <div class="login-intro">
        <h1 class="intro-title">
          <span class="intro-title-shine-wrap">
            <span class="intro-brand">自动化走查</span><span class="intro-cta">立即体验</span>
            <span class="intro-shine-bar" aria-hidden="true"></span>
          </span>
        </h1>
        <p class="intro-subtitle">一站式 UI 合规检测，助力提升设计还原度</p>
        <div class="intro-cards">
          <div class="intro-card">
            <span class="intro-card-icon" aria-hidden="true"><IconStroke name="baseline" size="md" /></span>
            <div class="intro-card-body">
              <h4>智能基准检测</h4>
              <p>支持多种模式，一键配置全局规范，自动校验页面合规性</p>
            </div>
          </div>
          <div class="intro-card">
            <span class="intro-card-icon" aria-hidden="true"><IconStroke name="palette" size="md" /></span>
            <div class="intro-card-body">
              <h4>视觉一致性分析</h4>
              <p>色盘、字体、间距、圆角等全维度对比，精准定位偏差</p>
            </div>
          </div>
          <div class="intro-card">
            <span class="intro-card-icon" aria-hidden="true"><IconStroke name="design" size="md" /></span>
            <div class="intro-card-body">
              <h4>设计稿还原度</h4>
              <p>AI 视觉差值分析，设计稿与实际页面智能对比</p>
            </div>
          </div>
          <div class="intro-card">
            <span class="intro-card-icon" aria-hidden="true"><IconStroke name="component" size="md" /></span>
            <div class="intro-card-body">
              <h4>组件级规范校验</h4>
              <p>按钮、表单、表格等组件细粒度检测</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：登录卡片 -->
      <div class="login-card-wrap">
        <div class="login-card">
          <h2>欢迎来到自动化走查平台</h2>
          <div class="auth-tabs">
            <div class="auth-tab" :class="{ active: isLogin }" @click="isLogin = true">账号登录</div>
            <div class="auth-tab" :class="{ active: !isLogin }" @click="isLogin = false">注册账号</div>
          </div>
          <div class="input-group">
            <label>账号名称</label>
            <input type="text" v-model="username" placeholder="请输入账号名称" autocomplete="username">
          </div>
          <div class="input-group">
            <label>密码</label>
            <input type="password" v-model="password" placeholder="请输入密码" @keyup.enter="handleSubmit">
          </div>
          <div class="input-group" v-if="!isLogin">
            <label>确认密码</label>
            <input type="password" v-model="confirmPassword" placeholder="请再次输入密码" @keyup.enter="handleSubmit">
          </div>
          <button class="btn-primary login-btn" @click="handleSubmit">{{ isLogin ? '登录' : '注册并登录' }}</button>
        </div>
      </div>
    </div>

    <footer class="login-footer">
      版权所有 © 中国移动云能力中心. 保留所有权利。
    </footer>
  </div>
</template>
  
  <script setup>
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  import IconStroke from '../components/IconStroke.vue'
  import { useUserStore } from '../store/user'
  import { showMsg } from '../utils/modal'
  import axios from 'axios'
  
  const router = useRouter()
  const userStore = useUserStore()
  const isLogin = ref(true)
  
  const username = ref('')
  const password = ref('')
  const confirmPassword = ref('')

  const goTo = (path) => router.push(path)

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
          showMsg('注册失败', res.data.message || '注册失败', 'error')
        }
      } catch (err) {
        const d = err.response?.data?.detail
        showMsg('注册失败', typeof d === 'string' ? d : '注册请求失败，请稍后再试', 'error')
      }
    }
  }
  </script>
  
  <style scoped>
.login-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 0;
  box-sizing: border-box;
  background-color: #f0f4ff;
  background-image: url('/images/login-bg.png');
  background-position: center center;
  background-size: cover;
  background-repeat: no-repeat;
  position: relative;
  overflow: hidden;
}

/* 1. 标题擦光效果：光带在文字上循环扫过 */
/* 擦光效果：光带仅在「自动化走查立即体验」9个字上扫过 */
.intro-title-shine-wrap {
  position: relative;
  display: inline-block;
  overflow: hidden;
}

.intro-shine-bar {
  position: absolute;
  top: 0;
  left: 0;
  width: 60px;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.7) 25%,
    rgba(255, 255, 255, 0.95) 50%,
    rgba(255, 255, 255, 0.7) 75%,
    transparent 100%
  );
  transform: translateX(-100%);
  animation: title-shine-sweep 3s ease-in-out infinite;
  pointer-events: none;
  mix-blend-mode: overlay;
}

@keyframes title-shine-sweep {
  0%, 100% { transform: translateX(-100%); }
  50% { transform: translateX(400%); }
}

/* 2. 底部水流涌动特效：紧贴页面最底部 */
.login-water-effect {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 140px;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
  /* 向下延伸至 safe-area，确保在刘海屏等设备上贴底 */
  height: calc(140px + env(safe-area-inset-bottom, 0px));
  bottom: calc(-1 * env(safe-area-inset-bottom, 0px));
}

.login-water-effect .wave {
  position: absolute;
  bottom: 0;
  left: 0;
  background-position: bottom center;
  width: 200%;
  height: 100%;
  background-repeat: repeat-x;
  background-size: 800px 100%;
  opacity: 0.4;
  will-change: transform;
}

.login-water-effect .wave-1 {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 120'%3E%3Cpath fill='%23c8d8f5' d='M0 60 Q200 20 400 60 T800 60 V120 H0 Z'/%3E%3C/svg%3E");
  animation: wave-flow 10s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.login-water-effect .wave-2 {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 120'%3E%3Cpath fill='%23b8ccf0' d='M0 70 Q200 30 400 70 T800 70 V120 H0 Z'/%3E%3C/svg%3E");
  animation: wave-flow 15s cubic-bezier(0.4, 0, 0.6, 1) infinite reverse;
  opacity: 0.35;
}

.login-water-effect .wave-3 {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 120'%3E%3Cpath fill='%23dce8ff' d='M0 50 Q200 90 400 50 T800 50 V120 H0 Z'/%3E%3C/svg%3E");
  animation: wave-flow 20s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  opacity: 0.3;
}

@keyframes wave-flow {
  0% { transform: translate3d(0, 0, 0); }
  100% { transform: translate3d(-800px, 0, 0); }
}

.login-water-effect .water-icon {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  z-index: 1;
  will-change: transform;
  animation: water-icon-float 6s ease-in-out infinite;
  /* 磨砂玻璃白：半透明白底 + 毛玻璃 */
  background: rgba(255, 255, 255, 0.45);
  border-radius: 50%;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.5);
}

.login-water-effect .water-icon :deep(svg) {
  width: 16px;
  height: 16px;
  stroke: url(#water-icon-gradient);
}

.login-water-effect .water-icon :deep(path),
.login-water-effect .water-icon :deep(rect),
.login-water-effect .water-icon :deep(circle) {
  stroke: url(#water-icon-gradient);
}

.water-icon-1 { left: 12%; bottom: 28%; animation-delay: 0s; }
.water-icon-2 { left: 38%; bottom: 45%; animation-delay: 1s; }
.water-icon-3 { left: 62%; bottom: 32%; animation-delay: 2s; }
.water-icon-4 { left: 85%; bottom: 52%; animation-delay: 2.5s; }

/* icon 随水流漂动：椭圆形轨迹，整体向左漂 + 上下起伏，首尾相接无跳变 */
@keyframes water-icon-float {
  0%, 100% { transform: translate(0, 0); opacity: 0.6; }
  25% { transform: translate(-10px, -5px); opacity: 0.78; }
  50% { transform: translate(-6px, -9px); opacity: 0.72; }
  75% { transform: translate(-2px, -4px); opacity: 0.8; }
}

.login-logo {
  position: absolute;
  z-index: 10;
  top: 24px;
  left: 32px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  font-size: 1rem;
  color: #1a1d2e;
  text-decoration: none;
  z-index: 10;
  transition: color 0.2s;
}

.login-logo:hover { color: #1A6AFF; }

.login-logo-icon {
  width: 34px;
  height: 34px;
  flex-shrink: 0;
  background: linear-gradient(145deg, #6366f1 0%, #4f6fff 45%, #1a6aff 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 1px 3px rgba(26, 106, 255, 0.25);
}

.login-logo-icon :deep(svg.logo-mark.icon-stroke) {
  display: block;
  width: 24px !important;
  height: 24px !important;
  transform: translateY(3px);
  color: #fff;
}

.login-logo-text { white-space: nowrap; }

.login-main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 60px;
  padding: 48px 32px 24px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  position: relative;
  z-index: 1;
}

.login-intro {
  flex: 1;
  max-width: 560px;
}

.intro-title {
  margin: 0 0 12px 0;
  font-size: 1.75rem;
  font-weight: 800;
  color: #1a1d2e;
  line-height: 1.3;
}

.intro-brand { color: #1a1d2e; }
.intro-cta { color: #ea580c; margin-left: 8px; }

.intro-subtitle {
  margin: 0 0 32px 0;
  font-size: 0.95rem;
  color: #6b7280;
  line-height: 1.5;
}

.intro-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.intro-card {
  display: flex;
  gap: 14px;
  padding: 18px 20px;
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 14px;
  box-shadow: 0 4px 20px rgba(15, 23, 42, 0.04);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease, background 0.2s ease;
  cursor: default;
}

.intro-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
  border-color: rgba(255, 255, 255, 0.75);
  background: rgba(255, 255, 255, 0.8);
}

.intro-card-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4b4b8b;
}

.intro-card-body h4 {
  margin: 0 0 6px 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: #1a1d2e;
}

.intro-card-body p {
  margin: 0;
  font-size: 0.8rem;
  color: #6b7280;
  line-height: 1.5;
}

.login-card-wrap {
  flex-shrink: 0;
  width: 100%;
  max-width: 420px;
}

.login-card {
  background: #fff;
  min-height: 460px;
  padding: 44px 40px 48px;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(15, 23, 42, 0.1);
  border: 1px solid #e8eaf0;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.login-card h2 {
  margin: 0 0 24px 0;
  font-size: 1.35rem;
  font-weight: 700;
  color: #1a1d2e;
  text-align: left;
}

.auth-tabs {
  display: flex;
  margin-bottom: 28px;
  border-bottom: 1px solid #e5e7eb;
}

.auth-tab {
  flex: 1;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #6b7280;
  font-size: 0.95rem;
  font-weight: 500;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: all 0.2s;
  text-align: center;
}

.auth-tab.active {
  color: #1A6AFF;
  border-bottom-color: #1A6AFF;
  font-weight: 700;
}

.input-group { text-align: left; margin-bottom: 22px; }
.input-group label { display: block; font-size: 0.8rem; color: #4b5563; margin-bottom: 8px; font-weight: 600; }
.input-group input {
  width: 100%;
  height: 44px;
  padding: 0 14px;
  border: 1px solid #e2e4ec;
  border-radius: 8px;
  outline: none;
  box-sizing: border-box;
  font-size: 0.95rem;
}

.input-group input:focus { border-color: #1A6AFF; }

.login-btn {
  width: 100%;
  height: 48px;
  padding: 0;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  background: #1A6AFF;
  color: white;
  margin-top: auto;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.login-btn:hover { background: #1557e6; }

.login-footer {
  padding: 16px 24px;
  text-align: center;
  font-size: 0.75rem;
  color: #9ca3af;
  position: relative;
  z-index: 1;
}

@media (max-width: 900px) {
  .login-main { flex-direction: column; gap: 32px; }
  .login-intro { max-width: 100%; }
  .intro-cards { grid-template-columns: 1fr; }
}
</style>