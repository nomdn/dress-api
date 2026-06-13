// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  routeRules: {
    '/**': { ssr: true },
  },
  modules: ['@element-plus/nuxt'],
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
  }
})
