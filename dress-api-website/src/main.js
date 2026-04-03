import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

import 'element-plus/theme-chalk/dark/css-vars.css'
import router from './router'
createApp(App).use(router).mount('#app')
