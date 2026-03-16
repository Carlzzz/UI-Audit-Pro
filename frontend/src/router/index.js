import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/login', component: () => import('../views/Login.vue') },
    { path: '/profile', component: () => import('../views/Profile.vue') }, // 个人信息
    { path: '/change-password', component: () => import('../views/ChangePassword.vue') }, // 修改密码
    { path: '/history', component: () => import('../views/History.vue') },
    { path: '/config', component: () => import('../views/Config.vue') },
    { path: '/scan', component: () => import('../views/Scan.vue') },
    { path: '/report', component: () => import('../views/Report.vue') },
    { path: '/audit-setup', component: () => import('../views/AuditSetup.vue') },
    { path: '/dashboard', component: () => import('../views/Dashboard.vue') }
  ]
})

import { useUserStore } from '../store/user'
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  if (to.path !== '/login' && !userStore.userInfo) {
    next('/login')
  } else {
    next()
  }
})

export default router