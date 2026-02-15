import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import VueLazyLoad from 'vue3-lazyload'
import 'element-plus/theme-chalk/dark/css-vars.css'
createApp(App).use(VueLazyLoad, {
  // options...;
  loading: '/lh_easy.webp',
  error:'error.svg',

}).use(ElementPlus).mount('#app')
