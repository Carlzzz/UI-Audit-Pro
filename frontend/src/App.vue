<template>
  <router-view></router-view>
</template>
<script setup>
import { onMounted } from 'vue'
import { useUserStore } from './store/user'
import axios from 'axios'

const userStore = useUserStore()

onMounted(async () => {
  if (userStore.userInfo) {
    try {
      const res = await axios.get('http://localhost:8000/api/user/' + userStore.userInfo.id)
      if (res.data.status === 'success') {
        userStore.login(res.data.data) // 更新本地存储的最新头像等
      }
    } catch (e) {
      console.warn('同步用户信息失败', e)
    }
  }
})
</script>
