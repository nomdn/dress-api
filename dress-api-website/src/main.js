import { createApp } from 'vue'
import { createHead } from '@unhead/vue/client'
import './style.css'
import App from './App.vue'
const head = createHead()

import 'element-plus/theme-chalk/dark/css-vars.css'
import router from './router'
createApp(App).use(router).use(head).mount('#app')
