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
v2的快速开始请看[v2](/v2/index.html)

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
   若跳过此步，API 将自动从 GitHub 加载远程索引（最小化模式）。

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
   FORCE_MINING=false
   AUTO_MINING_TIME=86400
   FORCE_REMOTE=false
   ```
   
  其中：
   
   **API_KEY**（必需）：API访问密钥，用于保护敏感操作如手动同步索引等
   
   **PORTS**：服务监听端口，默认8092
   
   **LOG_LEVEL**：日志级别，可选DEBUG/INFO/WARNING/ERROR，默认INFO
   
   **AUTO_SYNC**：是否启用自动同步功能，默认true
   
   **AUTO_SYNC_TIME**：自动同步间隔（秒），默认86400（24小时）
   
   **FORCE_MINING**：强制使用最小化模式（从CDN获取数据），默认false
   
   **FORCE_REMOTE**：强制使用远程预构建索引，默认false

5. 编译前端页面  
   ````bash
   cd dress-api-website
   npm i
   npm run build
   ````
5. 启动服务
   ```bash
   python main.py
   ```
   默认地址：`http://localhost:8092`

