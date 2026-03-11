<template>
  <nav class="app-navbar" :class="variant">
    <!-- Logo 品牌区 -->
    <a href="#" @click.prevent="goTo('/')" class="navbar-brand">
      <div class="logo-icon">✦</div>
      <span>{{ brandText }}</span>
    </a>

    <!-- 中间区域：导航链接 或 面包屑 或 自定义 slot -->
    <template v-if="variant === 'full'">
      <div class="navbar-nav">
        <a href="#" class="nav-link" :class="{ active: activeKey === 'scan' }" @click.prevent="goTo('/')">新建走查</a>
        <a href="#" class="nav-link" :class="{ active: activeKey === 'history' }" @click.prevent="goTo('/history')">历史记录</a>
        <a href="#" class="nav-link" :class="{ active: activeKey === 'config' }" @click.prevent="goTo('/config')">规范管理</a>
      </div>
    </template>
    <template v-else-if="variant === 'breadcrumb'">
      <div class="navbar-breadcrumb">
        <slot name="breadcrumb">
          <a href="#" @click.prevent="goTo('/')">首页</a>
          <span class="sep">/</span>
          <span class="cur">走查可视化看板</span>
        </slot>
      </div>
    </template>
    <template v-else-if="variant === 'scan'">
      <div class="navbar-task-id" v-if="$slots.taskId">
        <slot name="taskId"></slot>
      </div>
    </template>
    <!-- variant="report" / "custom"：无中间区，由 actions slot 填充右侧 -->

    <!-- 右侧区域 -->
    <div class="navbar-actions">
      <slot name="actions"></slot>

      <!-- 用户下拉（非 scan 页面显示） -->
      <div v-if="showUserDropdown" class="user-dropdown-container">
        <div v-if="showDropdown" class="dropdown-overlay" @click.stop="showDropdown = false"></div>
        <div class="avatar" @click="showDropdown = !showDropdown">
          {{ userStore.userInfo ? userStore.userInfo.avatar : '未' }}
        </div>
        <div class="dropdown-menu" v-if="showDropdown">
          <div class="dropdown-header">你好，{{ userStore.userInfo?.username }}</div>
          <div class="dropdown-item" @click="goTo('/profile')">👤 个人信息</div>
          <div class="dropdown-item" @click="goTo('/change-password')">🔒 修改密码</div>
          <div class="dropdown-divider"></div>
          <div class="dropdown-item text-danger" @click="handleLogout">🚪 退出登录</div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import { showConfirm } from '../utils/modal'

defineProps({
  /** full: 导航链接 | breadcrumb: 面包屑 | simple: 仅 Logo | scan: 扫描页 | custom: 完全自定义中间区 */
  variant: { type: String, default: 'full' },
  /** 导航高亮：scan | history | config */
  activeKey: { type: String, default: 'scan' },
  /** 品牌文字 */
  brandText: { type: String, default: '自动化走查工具' },
  /** 是否显示用户下拉 */
  showUserDropdown: { type: Boolean, default: true },
})

const router = useRouter()
const userStore = useUserStore()
const showDropdown = ref(false)

const goTo = (path) => router.push(path)
const handleLogout = async () => {
  const confirmed = await showConfirm('退出登录', '确定要退出当前账号吗？')
  if (confirmed) {
    userStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.app-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--nav-height);
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  padding: 0 24px;
  z-index: 1000;
  box-shadow: var(--shadow-sm);
}
.navbar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  font-size: 1rem;
  color: var(--text-primary);
  text-decoration: none;
  flex-shrink: 0;
}
.navbar-brand:hover { color: var(--primary); }
.logo-icon {
  width: 34px;
  height: 34px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
}
.navbar-nav {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: 28px;
}
.nav-link {
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  color: var(--text-secondary);
  text-decoration: none;
  transition: var(--transition);
}
.nav-link:hover { color: var(--primary); background: var(--primary-light); }
.nav-link.active { color: var(--primary); background: var(--primary-light); font-weight: 600; }
.navbar-breadcrumb {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: 16px;
  font-size: 0.85rem;
  color: var(--text-secondary);
}
.navbar-breadcrumb a { color: var(--primary); text-decoration: none; transition: var(--transition); }
.navbar-breadcrumb a:hover { color: var(--primary-dark); }
.navbar-breadcrumb .sep { color: var(--text-muted); margin: 0 2px; }
.navbar-breadcrumb .cur { color: var(--text-primary); font-weight: 600; }
.navbar-task-id { margin-left: 16px; font-size: 0.78rem; color: var(--text-muted); }
.navbar-task-id strong { color: var(--text-secondary); display: block; font-size: 0.82rem; }
.navbar-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 10px;
}
.user-dropdown-container { position: relative; }
.dropdown-overlay { position: fixed; inset: 0; z-index: 10; cursor: default; }
.avatar {
  width: 32px;
  height: 32px;
  background: var(--primary);
  border-radius: 50%;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: bold;
  cursor: pointer;
  transition: opacity 0.2s;
  position: relative;
  z-index: 20;
}
.avatar:hover { opacity: 0.9; }
.dropdown-menu {
  position: absolute;
  right: 0;
  top: calc(100% + 10px);
  background: white;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-md);
  width: 160px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 20;
}
.dropdown-header {
  padding: 12px 16px;
  font-size: 0.8rem;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border-light);
  background: var(--bg-page);
  font-weight: 600;
}
.dropdown-item {
  padding: 10px 16px;
  font-size: 0.85rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: background 0.15s;
}
.dropdown-item:hover { background: var(--primary-light); color: var(--primary); }
.dropdown-divider { height: 1px; background: var(--border); }
.dropdown-item.text-danger { color: var(--danger); }
.dropdown-item.text-danger:hover { background: #fef2f2; color: var(--danger); }
</style>
