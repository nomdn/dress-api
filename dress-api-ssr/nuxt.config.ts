import config from "./config/index";
// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  routeRules: {
    '/**': { ssr: true },
  },

  app: {
    head: {
      link: [
        { rel: 'icon', type: 'image/png', href: '/favicon.png' },
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
      ],
    },
  },
  modules: ['@element-plus/nuxt', '@nuxtjs/sitemap', '@nuxtjs/robots', '@vueuse/nuxt'],
  site:{
    name: 'Dress API',
    url: config.siteUrl,
  },
  robots:{
  },
  sitemap: {
    sources: [
      '/api/__sitemap__/urls',
    ]
  },

  vite: {
    optimizeDeps: {
      include: [
        '@element-plus/icons-vue',
        '@vueuse/core',
        'dayjs', // CJS
        'dayjs/plugin/*.js',
        'lodash-unified',
        'minidenticons',
      ]
    }
  },
  runtimeConfig: {
    remote: config.remote,
    rollback: config.rollback,
  },
  css: [
    // 1. 引入 Element Plus 基础样式 (如果你还没有引入的话)
    'element-plus/dist/index.css',
    
    // 2. 🌟 关键：引入 Element Plus 官方的暗黑模式 CSS 变量文件
    'element-plus/theme-chalk/dark/css-vars.css'
  ],
})