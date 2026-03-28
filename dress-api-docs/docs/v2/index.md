# 关于v2
虽然我不喜欢别人在文档写一大堆这个项目的前世今生  
但是这玩意太逆天了，所以还是写一个吧  

我是家里云享受者，在2026年的一天，我发现神秘的家里云老是神秘的失去ipv6  
重启又好了    
[柠檬监控](https://status.wsmdn.top)显示每天ipv6挂掉集中在`20:00~21:00`  
所以我设置了一个在`20:30`重启服务器的定时任务  
过了几天，我发现ipv6又在`17:00`挂掉了，导致dress-api后端直接挂了**3小时30分钟**  
所以我**忍无可忍**，在[三月七](https://mzh.moegirl.org.cn/%E4%B8%89%E6%9C%88%E4%B8%83)这个非常吉利的日子用`worker`技术栈重写了整个`DressAPI`  
但是qwen全系列模型都傻的一批 ~~阿里把是钱都拿去买推广了吗~~ 写出来的代码bug多的要命  
所以我不推荐你们用 ~~虽然我自己在用~~  
  
![一位好像在做慈善的公司的ceo](/cloudflare.webp)

点我一键部署：  

[![Deploy with Workers](https://deploy.workers.cloudflare.com/button)](https://deploy.workers.cloudflare.com/?url=https://github.com/nomdn/dress-api/tree/main/dress-api-worker)
---
Node.js推荐版本 : v22.18  
1. 克隆本项目
   ```bash
   git clone https://github.com/nomdn/dress-api.git
   cd dress-api
   cd dress-api-worker
   ```
2. 安装依赖
    ```bash
    npm i 
    ```
3. 登录到cloudflare
    ```bash
    npx wrangler login
    ```
4. 创建kv数据库
    ```bash
    npx wrangler kv:namespace create "DRESS_CACHE"
    ```
5. 绑定kv数据库
    `wrangler.jsonc`
    ``` json
    "kv_namespaces": [
		{
			"binding": "DRESS_CACHE",
			"id": "上一步中cli告诉你的id",
			"remote": true
		}
	]
    ```
6. 部署到worker
    ```bash
    npx wrangler deploy --minify
    ```
7. 设置环境变量（可选）
  在Cloudflare Workers控制台的设置页面中设置环境变量。
  ```` env
  URL_PREFIX: # url的前缀，索引中的图片path一般是"%23/447f.Misaka/obsolute/cthulhu.jpg" 要在前面加上图床链接如https://testingcf.jsdelivr.net/gh/Cute-Dress/Dress/ (末尾加"/"!)
  ````
## 调用示例

### 获取随机图片
```http
GET /v2/dress
```

#### 参数
- `num`：可选，指定返回数量，默认为 1
- `author`：可选，指定作者名称以获取该作者的图片

#### POST 请求支持
```http
POST /v2/dress
Content-Type: application/json

{
  "num": 5,
  "author": "Zhuge"
}
```

#### 响应示例

**单个结果（默认）：**
```json
{
  "author": "Mauve",
  "hash": "ae9f8020ff1bac84a2cb8953a8a1a6b8a1268bbb",
  "time": "2022-04-26T16:31:39+08:00",
  "url": "https://testingcf.jsdelivr.net/gh/Cute-Dress/Dress/M/Mauve/1st/3.jpeg",
  "notice": "Cute-Dress/Dress CC-BY-NC-SA 4.0"
}
```

**多个结果（当 num > 1 时）：**
```json
[
  {
    "author": "Mauve",
    "hash": "ae9f8020ff1bac84a2cb8953a8a1a6b8a1268bbb",
    "time": "2022-04-26T16:31:39+08:00",
    "url": "https://testingcf.jsdelivr.net/gh/Cute-Dress/Dress/M/Mauve/1st/3.jpeg",
    "notice": "Cute-Dress/Dress CC-BY-NC-SA 4.0"
  },
  {
    "author": "Zhuge",
    "hash": "9fdb945e66f93fd2f37862fcf5d3f4855512bc6b",
    "time": "2021-11-16T21:38:32+08:00",
    "url": "https://testingcf.jsdelivr.net/gh/Cute-Dress/Dress/A/Azhuquq/3.jpeg",
    "notice": "Cute-Dress/Dress CC-BY-NC-SA 4.0"
  }
]
```

### 健康检查
```http
GET /v2/health
```
响应示例：
```json
{"status": "ok"}
```
### 获取指定index

```http
GET /v2/index/{index_file}
```
index_file为索引代号，如id和author    

调用示例：
```http
GET https://api.wsmdn.top/v2/index/author
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


### 获取指定贡献者索引

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
GET https://api.wsmdn.top/v2/author/nekozzx
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

### 缓存说明
Dress API v2 版本使用 Cloudflare KV 存储进行缓存，缓存周期为 24 小时。系统会自动管理缓存以提高响应速度和可靠性。