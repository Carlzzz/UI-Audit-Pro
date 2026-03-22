import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './utils/modal.js' // SweetAlert2 样式 + 全局 mixin（先于 main.css 以便覆盖）
import './assets/main.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')