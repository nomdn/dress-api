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

		if (cachedID && cachedAuthor) {
			// 尝试解析缓存数据
			const indexID = JSON.parse(cachedID);
			const indexAuthor = JSON.parse(cachedAuthor);
			return { indexID, indexAuthor };
		}
	} catch (e) {
		
		console.warn("Failed to read or parse cache:", e);
	}
	const { indexID, indexAuthor } = await getIndex();

	// 更新缓存（即使为空也缓存，避免频繁请求）
	await env.DRESS_CACHE.put("indexID", JSON.stringify(indexID), { expirationTtl: CACHE_TTL });
	await env.DRESS_CACHE.put("indexAuthor", JSON.stringify(indexAuthor), { expirationTtl: CACHE_TTL });

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

app.get('/v2/dress', async (c) => {
	try {
		const { env } = c
		const urlPrefix = env.URL_PREFIX || 'https://testingcf.jsdelivr.net/gh/Cute-Dress/Dress/';
		var { indexID, indexAuthor } = await getCachedIndex(env);
		indexID = Object.values(indexID);
		const idLength = indexID.length;
		const randomIndex = getRandomIntInclusive(0, idLength - 1);
		const data = indexID[randomIndex];

		if (!data) {
		return c.json({ error: "Selected item is undefined" }, 500);
		}

		const author = data['author'] || 'Unknown';
		const hash = data['hash'] || '';
		const time = data['time'] || '';
		const pathVal = data['path'] || '';

		const path = `${urlPrefix}${pathVal}`;

		return c.json({
		author: author,
		hash: hash,
		time: time,
		url: path,
		notice: "Cute-Dress/Dress CC-BY-NC-SA 4.0",
		});

	} catch (err) {
		console.error("Handler error:", err);
		return c.json({ error: "Internal Server Error", message: err.message }, 500);
	}
});
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
app.get('/v2/author/:author', async (c) => {
	const author = c.req.param('author'); 
	const { indexID, indexAuthor } = await getCachedIndex(c.env)
	return c.json({ [author]: indexAuthor[author] });

});
export default app;