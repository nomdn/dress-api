---
outline: deep
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

演示站点：  
[前端+v1后端](https://dress.wsmdn.top)  
[v2后端](https://api.wsmdn.top/v2/health)  
# 请关注[柠檬博客](https://blog.wsmdn.dpdns.org)来获取服务变动信息！
https://blog.wsmdn.dpdns.org
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

## API 使用

### 获取随机图片
```http
GET /v1/dress
```

响应示例：
```json
{
  "img_url": "https://dress.wsmdn.top/img/X/Xiaoli_404/leg2.jpg",
  "img_author": "小离",
  "upload_time": "2019-03-30T19:30:34+08:00",
  "notice": "Cute-Dress/Dress CC BY-NC-SA 4.0"
}
```
最小化模式：
```json
{
  "img_url": "https://cdn.jsdelivr.net/gh/Cute-Dress/Dress@master/S/Satenruiko/IMG_20200302_231235.jpg",
  "img_author": "CuteDress",
  "upload_time": "2024-02-07T13:33:29+08:00",
  "notice": "Cute-Dress/Dress CC-BY-NC-SA 4.0"
}
```

### 手动同步（需 API Key）
```http
POST /v1/dress/sync
Header: X-API-Key: your_secret_key
```

### 健康检查
```http
GET /v1/health
```
响应示例：
```json
{
  "status": "healthy",
  "minimum_mode": "false",
  "auto_sync_enabled": "true",
  "auto_sync_time": 86700,
  "connectivity_to_gitHub": true,
  "connectivity_to_jsdelivr": true
}
```
### 获取指定index

```http
GET /v1/dress/index/{index_file}
```
index_file为索引文件名，如index_0.json和index_1.json    

调用示例：
```http
GET https://dress.wsmdn.top/v1/dress/index/index_1.json
```
返回示例：
```json
{
  "Vssblt": {
    "email": "root@host.localdomain",
    "contribution": [
      {
        "hash": "2721f9419822718965cca6bb8a46aa7c323f4396",
        "path": "%23/0xVssblt/2020-05-20/2.IMG_20200520.jpg",
        "time": "2020-05-21T01:39:14-04:00"
      },
      {
        "path": "%23/0xVssblt/2020-05-20/照骗.jpg",
        "time": "2020-05-21T01:39:14-04:00",
        "hash": "2721f9419822718965cca6bb8a46aa7c323f4396"
      },
      {
        "path": "%23/0xVssblt/第一次. 好羞涩啊(つ﹏⊂)/1. 第一次应该用什么姿势呢.jpg",
        "time": "2020-02-27T19:14:45+08:00",
        "hash": "dae8c2e74d3d6d7ffbc242d6d3dc9538e7ca96d0"
      },
      {
        "path": "%23/0xVssblt/第一次. 好羞涩啊(つ﹏⊂)/2. 摆个剪刀手吧.jpg",
        "time": "2020-02-27T19:14:45+08:00",
        "hash": "dae8c2e74d3d6d7ffbc242d6d3dc9538e7ca96d0"
      },
      {
        "path": "%23/0xVssblt/第一次. 好羞涩啊(つ﹏⊂)/3. 可惜镜子脏了.jpg",
        "time": "2020-02-27T19:14:45+08:00",
        "hash": "dae8c2e74d3d6d7ffbc242d6d3dc9538e7ca96d0"
      },
      {
        "path": "%23/0xVssblt/第二次. 越来越熟练了O(∩_∩)O/1. prprpr prprpr.jpg",
        "time": "2020-02-27T19:24:41+08:00",
        "hash": "647dba47b3eadbae0ccb3eceee6160fc2e6f2c0b"
      },
      {
        "path": "%23/0xVssblt/第二次. 越来越熟练了O(∩_∩)O/2. 过完年胖的只剩腿子了.jpg",
        "time": "2020-02-27T19:24:41+08:00",
        "hash": "647dba47b3eadbae0ccb3eceee6160fc2e6f2c0b"
      }
    ],
    "readme": "S/SnowyFox/README.md",
    "avatar_url": "https://avatars.githubusercontent.com/u/35415088?v=4?size=500",
    "github_username": "Vssblt"
  },
}
```


### 获取指定贡献者索引

```http
GET /v1/dress/author/{author}
```
author为作者名，如Satenruiko和CuteDress

调用实例
```` http
GET https://dress.wsmdn.top/v1/dress/author/nekozzx
````
响应示例：
```json
{
  "nekozzx": {
    "email": "3179579939@qq.com",
    "contribution": [
      {
        "hash": "4a7b97f152f02ba4cd0b76f6b80443d6f88f4f4b",
        "path": "Z/zzx/1.jpg",
        "time": "2026-02-25T13:02:58+08:00"
      },
      {
        "path": "Z/zzx/2.jpg",
        "time": "2026-02-25T13:02:58+08:00",
        "hash": "4a7b97f152f02ba4cd0b76f6b80443d6f88f4f4b"
      },
      {
        "path": "Z/zzx/3.jpg",
        "time": "2026-02-25T13:02:58+08:00",
        "hash": "4a7b97f152f02ba4cd0b76f6b80443d6f88f4f4b"
      },
      {
        "path": "Z/zzx/4.jpg",
        "time": "2026-02-25T13:02:58+08:00",
        "hash": "4a7b97f152f02ba4cd0b76f6b80443d6f88f4f4b"
      }
    ],
    "readme": "Z/zzx/README.md",
    "avatar_url": "https://avatars.githubusercontent.com/u/263363830?v=4?size=500",
    "github_username": "nekozzx"
  }
}
````
其中`readme`为贡献者自述，`avatar_url`为贡献者Github头像，`github_username`为贡献者的Github用户名  
这些参数**不一定**存在，调用时注意做判断