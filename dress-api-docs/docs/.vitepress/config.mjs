import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "DressAPI Docs",
  description: "DressAPI 文档",
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/' },
      { text: 'V2', link: '/v2/' }
    ],

    sidebar: [
      {
        text: '简介',
        items: [
          { text: '快速开始', link: '/introduction' },
          { text: 'v2文档', link: '/v2/'}
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/nomdn/dress-api' }
    ]
  }
})
