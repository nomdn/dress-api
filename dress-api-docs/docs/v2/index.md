---
next:
  text: '如何使用'
  link: '/v2/how-to-use'
---
# DressAPI v2
## 小故事
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
## 快速开始
可以使用**cloudflare**一键部署
[![Deploy with Workers](https://deploy.workers.cloudflare.com/button)](https://deploy.workers.cloudflare.com/?url=https://github.com/nomdn/dress-api/tree/main/dress-api-worker) 
KV数据库名记得改成**DRESS_CACHE**

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
