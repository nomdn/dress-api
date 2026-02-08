# Dress API 面向可爱的蓝孩子 (/ω＼) 的 随机图片API
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128+-red)

这是一个基于[Dress](https://github.com/Cute-Dress/Dress)的随机图片API  
演示API：https://dress.wsmdn.top  
文档：https://dress.wsmdn.top/docs

## 部署指南

最低Python版本：python3.8  

推荐Python版本：python3.12  

## 快速开始

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

5. 启动服务
   ```bash
   python main.py
   ```
   默认地址：http://localhost:8092

## API 使用

### 获取随机图片
```http
GET /dress/v1
```

响应示例：
```json
{
  "img_url": "http://localhost:8092/img/001.jpg",
  "img_author": ["作者A", "作者B"],
  "upload_time": "2024-02-07T13:33:29+08:00",
  "notice": "Cute-Dress/Dress CC BY-NC-SA 4.0"
}
```
最小化模式：
```json
{
  "img_url": "https://cdn.jsdelivr.net/gh/Cute-Dress/Dress@master/S/Satenruiko/IMG_20200302_231235.jpg",
  "img_author": "['CuteDress']",
  "upload_time": "2024-02-07T13:33:29+08:00",
  "notice": "Cute-Dress/Dress CC-BY-NC-SA 4.0"
}
```

### 手动同步（需 API Key）
```http
POST /dresses/v1/sync?rebuild_index=true
Header: X-API-Key: your_secret_key
```

### 健康检查
```http
GET /health
```

## 部署建议
- 生产环境：建议使用 `FORCE_MINING=true` + CDN 缓存
- Docker 支持：需通过 `-e ARK_API_KEY=xxx` 传入密钥
- 反向代理：可通过 Nginx/Apache 暴露 `/dress/v1` 路径

## 注意事项
本项目还未完善，不建议自己部署使用.  
如果你觉得我侵犯了您的权利，请在issues交流  
如果你想搭建完整版API请在项目根目录克隆[Dress](https://github.com/Cute-Dress/Dress)