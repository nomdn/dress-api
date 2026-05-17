# Dress API 面向可爱的蓝孩子 (/ω＼) 的 随机图片API
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128+-red)
[![Build and Commit Index](https://github.com/nomdn/dress-api/actions/workflows/build_index.yml/badge.svg)](https://github.com/nomdn/dress-api/actions/workflows/build_index.yml)
![Node.js](https://img.shields.io/badge/Node.js-22.18+-brightgreen)
![Vue](https://img.shields.io/badge/Vue-3.5.25-4FC08D?logo=vue.js)
![pnpm](https://img.shields.io/badge/pnpm-10-F69220?logo=pnpm)


这是一个基于[Dress](https://github.com/Cute-Dress/Dress)的随机图片API  
演示API：https://dress.wsmdn.top  
文档：https://docs.wsmdn.top



## 注意事项
演示站点极不稳定，建议自己部署   
如果你觉得我侵犯了您的权利，请在issues交流  
如果你想搭建完整版API请在项目根目录克隆[Dress](https://github.com/Cute-Dress/Dress)

## 包管理
本项目使用 **pnpm** 作为主要的包管理器（推荐），同时保留对 npm 的完全兼容。

### 方法一：pnpm（推荐）
```bash
# 安装 pnpm（如未安装）
npm install -g pnpm

# 安装依赖（根目录）
pnpm install

# 构建前端
cd dress-api-website && pnpm run build

# 部署 Worker
cd dress-api-worker && pnpm run deploy
```

### 方法二：npm（兼容）
```bash
# 安装依赖
npm install

# 构建前端
cd dress-api-website && npm run build

# 部署 Worker
cd dress-api-worker && npm run deploy
```

> 所有 GitHub Actions 工作流已统一使用 pnpm。

## 特别鸣谢
[Dress](https://github.com/Cute-Dress/Dress)  
整个项目都是基于这个图片库的  
[Flysky12138/PicW](https://github.com/Flysky12138/PicW)  
本项目的前端借鉴了这位大佬的设计(但是我没抄代码,因为我是MIT他是GPL)
## 友链
以下是一些基于dress-api的优秀项目  
<br>
[nonebot_plugin_simple_setu](https://github.com/nomdn/nonebot-plugin-simple-setu)  
<br>
欢迎所有使用dress-api的项目添加友链
