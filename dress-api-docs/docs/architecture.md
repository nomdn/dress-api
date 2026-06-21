# 架构说明

Dress API 是一个基于 [Dress](https://github.com/Cute-Dress/Dress) 图片库的随机图片API项目，由以下组件组成：

## 项目结构

```
dress-api/
├── main.py                 # v1 后端 (Python/FastAPI)
├── dress_tools.py          # v1 工具函数（索引获取、随机选取）
├── tools_v2.py             # 索引构建工具（扫描 Dress 仓库生成索引）
├── public/                 # 静态资源和索引文件
│   ├── index_0.json        # ID 索引（按数字ID键值）
│   └── index_1.json        # 作者索引（按作者名键值）
├── dress-api-worker/       # v2 后端 (Cloudflare Workers)
│   └── src/index.js        # Worker 入口，基于 Hono 框架
├── dress-api-ssr/          # v2 前端 (Nuxt 4 SSR)
│   └── app/                # Nuxt 应用目录
├── dress-api-website/      # v1 前端 (Vue 3 SPA)
│   └── src/                # Vue 应用目录
└── dress-api-docs/         # 文档站点 (VitePress)
    └── docs/               # Markdown 文档
```

## 数据流

```
┌─────────────────┐     git clone/pull      ┌──────────────────┐
│  Dress 图片仓库  │ ◄──────────────────── │  tools_v2.py     │
│ (Cute-Dress/Dress)│                        │  扫描仓库生成索引  │
└─────────────────┘                         └────────┬─────────┘
                                                     │
                                                     ▼
                                          ┌──────────────────┐
                                          │  index_0.json    │
                                          │  index_1.json    │
                                          │  (public/ 目录)   │
                                          └────────┬─────────┘
                                                   │
                           ┌───────────────────────┼───────────────────────┐
                           │                       │                       │
                           ▼                       ▼                       ▼
                  ┌────────────────┐     ┌────────────────┐     ┌────────────────┐
                  │ v1 FastAPI 后端 │     │ v2 Worker 后端  │     │ jsDelivr CDN   │
                  │  (main.py)     │     │ (src/index.js) │     │ (备用数据源)    │
                  └───────┬────────┘     └───────┬────────┘     └────────────────┘
                          │                       │
                          ▼                       ▼
                  ┌────────────────┐     ┌────────────────┐
                  │ v1 Vue 前端    │     │ v2 Nuxt SSR 前端│
                  │ (dress-api-    │     │ (dress-api-ssr) │
                  │  website)      │     │                 │
                  └────────────────┘     └─────────────────┘
```

## 索引格式

### index_0.json（ID 索引）

按数字ID键值的图片元数据：

```json
{
  "0": {
    "author": "nekozzx",
    "hash": "4a7b97f...",
    "path": "Z/zzx/1.jpg",
    "time": "2026-02-25T13:02:58+08:00"
  },
  "1": { ... }
}
```

### index_1.json（作者索引）

按作者名键值的图片元数据，包含作者信息：

```json
{
  "nekozzx": {
    "email": "...",
    "avatar_url": "https://avatars.githubusercontent.com/...",
    "github_username": "nekozzx",
    "readme": "Z/zzx/README.md",
    "contribution": [
      {
        "hash": "4a7b97f...",
        "path": "Z/zzx/1.jpg",
        "time": "2026-02-25T13:02:58+08:00"
      }
    ]
  }
}
```

## 版本对比

| 特性 | v1 (FastAPI) | v2 (Cloudflare Workers) |
|------|-------------|------------------------|
| 运行环境 | 自托管服务器 | Cloudflare 边缘网络 |
| 数据存储 | 本地文件 + git pull | Cloudflare KV 缓存 |
| 索引更新 | 定时同步 (默认24h) | KV 缓存过期自动刷新 (24h) |
| 部署方式 | `python main.py` | `wrangler deploy` |
| 费用 | 服务器费用 | Cloudflare 免费计划 |
| 状态 | 已停维 | 活跃维护 |

## 前端说明

### dress-api-website (v1 前端)

- 技术栈：Vue 3 + Vite + Element Plus
- 构建输出到 `../public`，由 FastAPI 静态文件服务托管
- 支持暗色模式、响应式布局、作者搜索和分页

### dress-api-ssr (v2 前端)

- 技术栈：Nuxt 4 + Element Plus + VueUse
- 服务端渲染 (SSR)，对 SEO 友好
- 支持暗色模式、响应式布局、作者详情页（Markdown 渲染）
- 部署在 Cloudflare Workers

## 图片许可

所有图片来自 [Cute-Dress/Dress](https://github.com/Cute-Dress/Dress) 仓库，遵循 [CC-BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可协议。

API 响应中的 `notice` 字段包含此许可信息。
