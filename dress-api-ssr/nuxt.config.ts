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
  modules: ['@element-plus/nuxt', '@nuxtjs/seo', '@nuxtjs/sitemap', '@nuxtjs/robots'],
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
})