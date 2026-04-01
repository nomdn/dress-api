/**
 * Welcome to Cloudflare Workers!
 */
import { Hono } from 'hono';
import { cors } from 'hono/cors';

// 全局变量（在 Isolate 生命周期内持久存在）
const CACHE_TTL = 24 * 60 * 60; // 缓存 24 小时
async function getCachedIndex(env) {
	try {
		// 正确 await 异步 get
		const cachedID = await env.DRESS_CACHE.get("indexID");
		const cachedAuthor = await env.DRESS_CACHE.get("indexAuthor");
		const cachedTimestamp = await env.DRESS_CACHE.get("indexTimestamp");

		// 检查缓存是否存在且未过期
		if (cachedID && cachedAuthor && cachedTimestamp) {
			const timestamp = parseInt(cachedTimestamp);
			const now = Math.floor(Date.now() / 1000);
			
			// 检查缓存是否过期
			if (now - timestamp < CACHE_TTL) {
				// 尝试解析缓存数据
				const indexID = JSON.parse(cachedID);
				const indexAuthor = JSON.parse(cachedAuthor);
				return { indexID, indexAuthor };
			}
		}
	} catch (e) {
		
		console.warn("Failed to read or parse cache:", e);
	}
	const { indexID, indexAuthor } = await getIndex();

	// 更新缓存（即使为空也缓存，避免频繁请求）
	const timestamp = Math.floor(Date.now() / 1000);
	// 使用 expiration 选项设置绝对过期时间，确保过期时间准确
	const expiration = timestamp + CACHE_TTL;
	await env.DRESS_CACHE.put("indexID", JSON.stringify(indexID), { expiration });
	await env.DRESS_CACHE.put("indexAuthor", JSON.stringify(indexAuthor), { expiration });
	await env.DRESS_CACHE.put("indexTimestamp", timestamp.toString(), { expiration });

	return { indexID, indexAuthor };

}
// ✅ 移除 axios，改用原生 fetch
async function getIndex() {
	try {
		// 并行请求两个文件
		const [res1, res2] = await Promise.all([
		fetch("https://testingcf.jsdelivr.net/gh/nomdn/dress-api@main/public/index_0.json"),
		fetch("https://testingcf.jsdelivr.net/gh/nomdn/dress-api@main/public/index_1.json")
		]);

		if (!res1.ok || !res2.ok) {
		throw new Error(`Fetch failed: ${res1.status} / ${res2.status}`);
		}
		const indexID = await res1.json();
		const indexAuthor = await res2.json();

		return { indexID, indexAuthor };
	} catch (error) {
		console.error("Error in getIndex:", error);
		// 即使出错也返回空数组，防止崩溃
		return { indexID: {}, indexAuthor: {} };
	}
}

function getRandomIntInclusive(min, max) {
	const minCeiled = Math.ceil(min);
	const maxFloored = Math.floor(max);
	return Math.floor(Math.random() * (maxFloored - minCeiled + 1) + minCeiled);
}

const app = new Hono();
app.use('*', cors());

app.get('/', (c) => c.redirect('https://dress.wsmdn.top/', 302));

// 处理 /v2/dress 端点的共享函数
async function handleDressRequest(c) {
	// 从请求体或查询参数获取参数
	let num = parseInt(c.req.query('num') || '1');
	let authorParam = c.req.query('author');
	let authors = [];
	
	if (c.req.method === 'POST') {
		try {
			const body = await c.req.json();
			num = parseInt(body.num || num);
			authorParam = body.author || authorParam;
			if (typeof authorParam === 'string') {
				authors = [authorParam]; // 如果是单个字符串，转换为列表
			} else if (Array.isArray(authorParam)) {
				authors = authorParam;
			}
		} catch (e) {
			// 忽略解析错误
		}
	} else if (c.req.method === 'GET') {
		if (authorParam) {
			authors = authorParam.split('|');
		}
	}
	
	try {
		const { env } = c
		const urlPrefix = env.URL_PREFIX || 'https://testingcf.jsdelivr.net/gh/Cute-Dress/Dress/';
		var { indexID, indexAuthor } = await getCachedIndex(env);
		indexID = Object.values(indexID);
		const idLength = indexID.length;
		
		// 确保num不超过最大值
		let maxNum = Math.min(num, idLength);
		const results = [];
		const usedPaths = new Set(); // 用于存储已使用的path，确保不重复
		
		if (authors.length > 0) {
			// 检查所有作者是否存在，并计算总贡献数
			let authorAllCount = 0;
			for (const oneAuthor of authors) {
				if (indexAuthor[oneAuthor]) {
					authorAllCount += indexAuthor[oneAuthor]["contribution"].length;
				} else {
					return c.json({ error: `Author ${oneAuthor} not found` }, 404);
				}
			}
			
			// 确保num不超过总贡献数
			maxNum = Math.min(num, authorAllCount);
			
			// 随机选择num个不同的图片
			while (results.length < maxNum) {
				// 随机选择一个作者
				const randomAuthor = authors[getRandomIntInclusive(0, authors.length - 1)];
				const authorData = indexAuthor[randomAuthor];
				const contributions = authorData["contribution"];
				
				if (contributions.length > 0) {
					// 随机选择一个贡献
					const randomIndex = getRandomIntInclusive(0, contributions.length - 1);
					const entry = contributions[randomIndex];
					
					if (!usedPaths.has(entry["path"])) {
						usedPaths.add(entry["path"]);
						const author = randomAuthor;
						const hash = entry['hash'] || '';
						const time = entry['time'] || '';
						const pathVal = entry['path'] || '';
						const path = `${urlPrefix}${pathVal}`;
						
						results.push({
							author: author,
							hash: hash,
							time: time,
							url: path,
							notice: "Cute-Dress/Dress CC-BY-NC-SA 4.0",
						});
					}
				}
			}
		} else {
			// 随机选择num个不同的图片
			while (results.length < maxNum) {
				const randomIndex = getRandomIntInclusive(0, idLength - 1);
				const data = indexID[randomIndex];
				if (data && !usedPaths.has(data["path"])) {
					usedPaths.add(data["path"]);
					const author = data['author'] || 'Unknown';
					const hash = data['hash'] || '';
					const time = data['time'] || '';
					const pathVal = data['path'] || '';
					const path = `${urlPrefix}${pathVal}`;
					
					results.push({
						author: author,
						hash: hash,
						time: time,
						url: path,
						notice: "Cute-Dress/Dress CC-BY-NC-SA 4.0",
					});
				}
			}
		}
		
		// 如果只请求一个，返回单个对象，保持向后兼容
		if (num === 1 && results.length > 0) {
			return c.json(results[0]);
		}
		return c.json(results);

	} catch (err) {
		console.error("Handler error:", err);
		return c.json({ error: "Internal Server Error", message: err.message }, 500);
	}
}

// 注册 GET 和 POST 路由
app.get('/v2/dress', handleDressRequest);
app.post('/v2/dress', handleDressRequest);
app.get('/v2/health', async (c) => { 
	return c.json({ status: "ok" });
});

app.get('/v2/index/:index', async (c) => {
	const index = c.req.param('index'); 
	const { indexID, indexAuthor } = await getCachedIndex(c.env)
	if (index === 'id') {
		return c.json(indexID);
	} else if (index === 'author') {
		return c.json(indexAuthor);
	} else {
		return c.json({ error: "Invalid index" }, 400);
	}

});
app.post('/v2/index/:index', async (c) => {
	const index = c.req.param('index'); 
	const { indexID, indexAuthor } = await getCachedIndex(c.env)
	if (index === 'id') {
		return c.json(indexID);
	} else if (index === 'author') {
		return c.json(indexAuthor);
	} else {
		return c.json({ error: "Invalid index" }, 400);
	}

});

app.get('/v2/author/:author', async (c) => {
	const author = c.req.param('author'); 
	const { indexID, indexAuthor } = await getCachedIndex(c.env)
	return c.json({ [author]: indexAuthor[author] });

});
app.post('/v2/author/:author', async (c) => {
	const author = c.req.param('author'); 
	const { indexID, indexAuthor } = await getCachedIndex(c.env)
	return c.json({ [author]: indexAuthor[author] });

});
export default app;