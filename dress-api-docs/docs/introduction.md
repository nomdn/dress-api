---
outline: deep

next:
  text: '如何使用'
  link: '/how-to-use'

---

# 关于Dress API

Dress API 是一个基于Dress的随机图片API，提供**随机图片、图片作者、图片上传时间、图片版权**等信息。  

支持多种方案部署，如：  Cloudflare Workers，Python手动部署

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128+-red)
[![Build and Commit Index](https://github.com/nomdn/dress-api/actions/workflows/build_index.yml/badge.svg)](https://github.com/nomdn/dress-api/actions/workflows/build_index.yml)
![Node.js](https://img.shields.io/badge/Node.js-22.18+-brightgreen)
![Vue](https://img.shields.io/badge/Vue-3.5.25-4FC08D?logo=vue.js)

> [!TIP]
> v1演示站点部署在不稳定的机器上v2部署在免费计划的worker上，我在这里强烈建议您自己部署使用！！

 
> [!NOTE]
> 请关注[柠檬博客](https://blog.wsmdn.dpdns.org)来获取服务变动信息！
> https://blog.wsmdn.top

演示站点：  
[前端+v1后端](https://dress.wsmdn.top)  
[v2后端](https://api.wsmdn.top/v2/health) 

## 快速开始

该项目有v1和v2两个版本  
其中v2基于`cloudflare worker`和 `worker kv`  
v1基于`python`和`fastapi`  
下列步骤是**v1**的快速开始   
v2的快速开始请看[v2](./v2/index.md)

---
最低Python版本：python3.8  
推荐Python版本：python3.12  
Node.js推荐版本 : v22.18  

1. 克隆本项目
   ```bash
   git clone https://github.com/nomdn/dress-api.git
   cd dress-api
   ```
   
2. （可选）拉取 Dress 图片库
   ```bash
   git clone https://github.com/Cute-Dress/Dress public
   ```
   若跳过此步，API 将自动从 GitHub 加载远程索引（轻量模式）。

3. 安装依赖
   ```bash
   python -m venv .venv
   # Linux/macOS:
   source .venv/bin/activate
   # Windows (PowerShell):
   .venv\Scripts\activate
   
   pip install -r requirements.txt
   ```

4. 配置环境变量（创建 .env 文件）
   ```ini
   API_KEY=your_secret_key
   PORTS=8092
   LOG_LEVEL=INFO
   AUTO_SYNC=true
   AUTO_SYNC_TIME=86400
   FORCE_LITE=false
   FORCE_REMOTE=false
   ```
   
  其中：
   
   **API_KEY**（必需）：API访问密钥，用于保护敏感操作如手动同步索引等
   
   **PORTS**：服务监听端口，默认8092
   
   **LOG_LEVEL**：日志级别，可选DEBUG/INFO/WARNING/ERROR，默认INFO
   
   **AUTO_SYNC**：是否启用自动同步功能，默认true
   
   **AUTO_SYNC_TIME**：自动同步间隔（秒），默认86400（24小时）
   
   **FORCE_LITE**：强制使用轻量模式（从CDN获取数据），默认false
   
   **FORCE_REMOTE**：强制使用远程预构建索引，默认false

5. 配置前端页面
`src/config/index.js`  
```` javascript
/**
 * Dress API 客户端配置
 * 
 * 该配置用于控制前端如何与 Dress 图片服务交互。
 * - `useMinimum`: 启用“最简模式”（Minimal Mode），此时完全依赖远程 API，不使用本地资源。
 * - `remote`: 主服务地址（推荐使用，响应更快、功能完整）。
 * - `rollback`: 回退地址（当主服务不可用时可手动切换，通常指向 jsDelivr CDN）。
 */
const config = {
    // 是否启用最简模式（Minimal Mode）：
    // - true: 所有数据和图片均从 remote 或 rollback 指定的远程 URL 获取
    // - false: 可能尝试使用本地托管的资源（需配合后端非 minimal_mode）
    useLite: false,

    // 主服务配置（生产环境推荐地址）
    remote: {
        remoteURL: 'https://dress.wsmdn.top/',     // API 根地址
        imgURL: 'https://dress.wsmdn.top/img/'     // 本地托管图片的访问前缀（仅在非 minimal 模式下有效）
    },

    // 回退服务配置（CDN 备用地址，适用于主服务宕机或网络受限场景）
    rollback: {
        remoteURL: 'https://testingcf.jsdelivr.net/gh/nomdn/dress-api@main/',
        imgURL: 'https://testingcf.jsdelivr.net/gh/Cute-Dress/Dress@master/'
    }
};

export default config;
````
 6. 编译前端页面  
    ````bash
    cd dress-api-website
    # 方法一：pnpm（推荐）
    pnpm install
    pnpm run build
    # 方法二：npm（兼容）
    # npm install
    # npm run build
    ````
7. 启动服务
   ```bash
   python main.py
   ```
   默认地址：`http://localhost:8092`

