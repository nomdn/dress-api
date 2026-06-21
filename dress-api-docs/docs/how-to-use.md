---
next:
  text: 'v2文档'
  link: '/v2'
prev:
  text: '快速开始'
  link: '/introduction'
---
# API 使用

API V1:  
````text
# 已关停
https://dress.wsmdn.top/v1/dress
````
## 获取随机图片
```http
GET /v1/dress
```

### 参数
- `num`：可选，指定返回数量，默认为 1
- `author`：可选，指定作者名称以获取该作者的图片

### POST 请求支持
```http
POST /v1/dress
Content-Type: application/json

{
  "num": 5,
  "author": "Zhuge"
}
```

### 响应示例

**单个结果（默认）：**
```json
{
  "url": "https://dress.wsmdn.top/img/L/LF112/LF112_Dress%232019_1.jpg",
  "author": "“LF112”",
  "hash": "2855ae71bd46bb84b2124577f941bb4c922587cc",
  "time": "2019-03-15T23:18:48+08:00",
  "notice": "Cute-Dress/Dress CC-BY-NC-SA 4.0"
}
```

**多个结果（当 num > 1 时）：**
```json
[
  {
    "url": "https://dress.wsmdn.top/img/Z/zzx/3.jpg",
    "author": "nekozzx",
    "hash": "4a7b97f152f02ba4cd0b76f6b80443d6f88f4f4b",
    "time": "2026-02-25T13:02:58+08:00",
    "notice": "Cute-Dress/Dress CC-BY-NC-SA 4.0"
  },
  {
    "url": "https://dress.wsmdn.top/img/Z/zzx/1.jpg",
    "author": "nekozzx",
    "hash": "4a7b97f152f02ba4cd0b76f6b80443d6f88f4f4b",
    "time": "2026-02-25T13:02:58+08:00",
    "notice": "Cute-Dress/Dress CC-BY-NC-SA 4.0"
  }
]
```

**最小化模式：**
```json
{
  "url": "https://dress.wsmdn.top/img/Z/zzx/1.jpg",
  "author": "nekozzx",
  "hash": "4a7b97f152f02ba4cd0b76f6b80443d6f88f4f4b",
  "time": "2026-02-25T13:02:58+08:00",
  "notice": "Cute-Dress/Dress CC-BY-NC-SA 4.0"
}
```

## 手动同步（需 API Key）
```http
POST /v1/dress/sync
Header: X-API-Key: your_secret_key
```

## 健康检查
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
## 获取指定index

```http
GET /v1/dress/index/{index_file}
```
index_file为索引文件名，如index_0.json和index_1.json    

### POST 请求支持
```http
POST /v1/dress/index/{index_file}
Content-Type: application/json
```

### 调用示例：
```http
GET https://dress.wsmdn.top/v1/dress/index/index_1.json
```

### 返回示例：
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
  }
}
```


### 获取指定贡献者索引

```http
GET /v1/dress/author/{author}
```

#### POST 请求支持
```http
POST /v1/dress/author/{author}
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