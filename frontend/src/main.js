import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './assets/main.css' // 引入你的全局样式

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')