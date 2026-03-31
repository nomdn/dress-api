---
prev:
  text: '快速开始'
  link: '/v2/'
---
# 调用示例
API V2:  
````text
https://api.wsmdn.top/v2/dress
````
## 获取随机图片
```http
GET /v2/dress
```

### 参数
- `num`：可选，指定返回数量，默认为 1
- `author`：可选，指定作者名称以获取该作者的图片

### POST 请求支持
```http
POST /v2/dress
Content-Type: application/json

{
  "num": 5, # 可选，默认为1，指定返回图片的数量
  "author": "nekozzx" # 可选,指定返回某个贡献者的图片
}
```

### 响应示例


``` http
GET /v2/dress
```
**单个结果（默认）：**
```json
    {
    "author": "nekozzx",
    "hash": "4a7b97f152f02ba4cd0b76f6b80443d6f88f4f4b",
    "time": "2026-02-25T13:02:58+08:00",
    "url": "https://testingcf.jsdelivr.net/gh/Cute-Dress/Dress/Z/zzx/4.jpg",
    "notice": "Cute-Dress/Dress CC-BY-NC-SA 4.0"
    }
```

**多个结果（当 num > 1 时）：**
```json
[
  {
    "author": "nekozzx",
    "hash": "4a7b97f152f02ba4cd0b76f6b80443d6f88f4f4b",
    "time": "2026-02-25T13:02:58+08:00",
    "url": "https://testingcf.jsdelivr.net/gh/Cute-Dress/Dress/Z/zzx/3.jpg",
    "notice": "Cute-Dress/Dress CC-BY-NC-SA 4.0"
  },
  {
    "author": "nekozzx",
    "hash": "4a7b97f152f02ba4cd0b76f6b80443d6f88f4f4b",
    "time": "2026-02-25T13:02:58+08:00",
    "url": "https://testingcf.jsdelivr.net/gh/Cute-Dress/Dress/Z/zzx/1.jpg",
    "notice": "Cute-Dress/Dress CC-BY-NC-SA 4.0"
  }
]
```
**指定作者**  
``` http
GET /v2/dress?author=nekozzx
```
**POST请求**
```http
POST /v2/dress
Content-Type: application/json
{
  "author": "nekozzx"
}
```
**响应示例**
``` json
  {
    "author": "nekozzx",
    "hash": "4a7b97f152f02ba4cd0b76f6b80443d6f88f4f4b",
    "time": "2026-02-25T13:02:58+08:00",
    "url": "https://testingcf.jsdelivr.net/gh/Cute-Dress/Dress/Z/zzx/3.jpg",
    "notice": "Cute-Dress/Dress CC-BY-NC-SA 4.0"
  },
```
**多返回**
```http
GET /v2/dress?num=5
```
**POST请求**
```http
POST /v2/dress
Content-Type: application/json
{
  "num": 5,
}
```
**返回示例**
```json
  [
    {
        "author": "hotspringGG",
        "hash": "c8a225d74017dba55d89bbdee39959ba6ebdb7c7",
        "time": "2022-07-29T11:44:35+08:00",
        "url": "https://testingcf.jsdelivr.net/gh/Cute-Dress/Dress/H/Hotspring/B68EC118C80B067D349C2426A9ADD5B4.jpg",
        "notice": "Cute-Dress/Dress CC-BY-NC-SA 4.0"
    },
    {
        "author": "Neko3000",
        "hash": "016544fbea6e1c014f5afa3b421c1241ed778ae4",
        "time": "2020-01-02T20:30:57+08:00",
        "url": "https://testingcf.jsdelivr.net/gh/Cute-Dress/Dress/N/Neko3000/20191222_113053237_iOS.jpg",
        "notice": "Cute-Dress/Dress CC-BY-NC-SA 4.0"
    },
    {
        "author": "Kisechan",
        "hash": "d6642705917ad84eb9511646633294cbed4056a6",
        "time": "2025-11-05T22:23:01+08:00",
        "url": "https://testingcf.jsdelivr.net/gh/Cute-Dress/Dress/K/kiseplatinyl/水手服/7.jpg",
        "notice": "Cute-Dress/Dress CC-BY-NC-SA 4.0"
    },
    {
        "author": "hly0928",
        "hash": "b17be79fc8682500cbc94107e77a57d825b34c7d",
        "time": "2019-06-11T06:05:53+08:00",
        "url": "https://testingcf.jsdelivr.net/gh/Cute-Dress/Dress/H/hly0928/02.jpeg",
        "notice": "Cute-Dress/Dress CC-BY-NC-SA 4.0"
    },
    {
        "author": "16061169",
        "hash": "1edbc2f3e36a38c842c2821d0ee6af55817c800c",
        "time": "2020-09-11T18:37:44+08:00",
        "url": "https://testingcf.jsdelivr.net/gh/Cute-Dress/Dress/N/noharaShio/nobun.jpg",
        "notice": "Cute-Dress/Dress CC-BY-NC-SA 4.0"
    }
  ]
```
## 健康检查
```http
    GET /v2/health
```
响应示例：
```json
{"status": "ok"}
```
## 获取指定index

```http
GET /v2/index/{index_file}
```
index_file为索引代号，如id和author    

调用示例：
```http
GET /v2/index/author
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
  }
}
```
**POST请求支持**
```http
POST /v2/index/author
```
**响应示例**
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

## 获取指定贡献者索引

```http
GET /v2/author/{author}
```

#### POST 请求支持
```http
POST /v2/author/{author}
```

author为作者名，如Satenruiko和CuteDress

调用实例
```` http
GET /v2/author/nekozzx
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
**POST请求支持**  
请求示例
```http
POST /v2/author/nekozzx
```
**响应示例**
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

### 缓存说明
Dress API v2 版本使用 Cloudflare KV 存储进行缓存，缓存周期为 24 小时。系统会自动管理缓存以提高响应速度和可靠性。