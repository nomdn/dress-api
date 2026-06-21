import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "DressAPI Docs",
  description: "DressAPI 文档",
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }]
  ],
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/' },
      { text: 'V2文档', link: '/v2/' },
      { text: '架构说明', link: '/architecture' }
    ],

    sidebar: [
      {
        text: "v2文档（推荐）",
        items: [
          {
            text: "快速开始",
            link: "/v2/"
          },
          {
            text: "使用指南",
            link: "/v2/how-to-use/"
          }
        ]
      },
      {
        text: "v1文档（已停维）",
        items: [
          {
            text: "快速开始",
            link: "/introduction/"
          },
          {
            text: "使用指南",
            link: "/how-to-use/"
          }
        ]
      },
      {
        text: "其他",
        items: [
          {
            text: "架构说明",
            link: "/architecture"
          }
        ]
      }

    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/nomdn/dress-api' }
    ],
        
    editLink: {
      pattern: 'https://github.com/nomdn/dress-api/edit/main/dress-api-docs/docs/:path',
      text: 'Edit this page on GitHub'
    },
    footer: {
      message: 'MIT协议下发布 <a href="https://beian.miit.gov.cn/">苏ICP备2026012471号</a>',
      copyright: '版权所有 © 2026-现在 nomdn'
    },
    
  },
  sitemap: {
    hostname: 'https://docs.wsmdn.top',
    lastmodDateOnly: false
  },
  lastUpdated: true
})
