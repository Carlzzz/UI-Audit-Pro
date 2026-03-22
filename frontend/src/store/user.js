import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    userInfo: JSON.parse(localStorage.getItem('userInfo') || 'null')
  }),
  actions: {
    login(data) {
      this.userInfo = data
      localStorage.setItem('userInfo', JSON.stringify(data))
    },
    logout() {
      this.userInfo = null
      localStorage.removeItem('userInfo')
    },
    updateAvatar(newAvatar) {
      if (this.userInfo) {
        this.userInfo.avatar = newAvatar
        localStorage.setItem('userInfo', JSON.stringify(this.userInfo))
      }
    },
    updateUserInfo(partial) {
      if (this.userInfo && partial && typeof partial === 'object') {
        Object.assign(this.userInfo, partial)
        localStorage.setItem('userInfo', JSON.stringify(this.userInfo))
      }
    }
  }
})