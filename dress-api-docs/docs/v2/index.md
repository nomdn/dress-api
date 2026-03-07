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
## 调用示例

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
s

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
GET /v2/dress/index/{index_file}
```
index_file为索引文件名，如index_0.json和index_1.json    

调用示例：
```http
GET https://api.wsmdn.top/v2/dress/index/index_1.json
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
GET /v2/author/{author}
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