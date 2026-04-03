import os
from pathlib import Path as p_pathlib
import subprocess
import random
import json
from typing import Annotated
import httpx
import colorama
from colorama import Fore, Style
import uvicorn
import logging
from dotenv import load_dotenv
from git import Repo
import asyncio
import json
from fastapi import (
    FastAPI,
    Response,
    Request,
    BackgroundTasks,
    HTTPException,
    Header,
    Query,
    Path,
    status
)
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from urllib.parse import urljoin, urlparse
from httpx import TimeoutException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager  # 添加这个导入
from dress_tools import run_git_pull, get_github_index,random_pick,random_pick_author
from tools_v2 import build_index_by_author, convert_index_author_to_index_id



index_author = {}
index_id = {}
jsdelivr_ok = False
github_ok = False
API_KEY = "admin"
ports = 8092
log_level = "INFO"
auto_sync_enabled = "true"
auto_sync_time = 86400  # 默认24小时
minimum_mode = "false"
force_remote_index = "false"
# 统一加载逻辑
load_dotenv()  # 先加载 .env

API_KEY = os.environ.get("API_KEY") or API_KEY
ports = int(os.environ.get("PORTS") or ports)
log_level = os.environ.get("LOG_LEVEL") or log_level
auto_sync_enabled = os.environ.get("AUTO_SYNC") or auto_sync_enabled
auto_sync_time = int(os.environ.get("AUTO_SYNC_TIME") or auto_sync_time)
minimum_mode = os.environ.get("FORCE_MINING") or minimum_mode
force_remote_index = os.environ.get("FORCE_REMOTE") or force_remote_index

# 安全地设置日志级别，处理None值和无效值
if log_level is None:
    log_level = "INFO"
try:
    log_level_value = getattr(logging, log_level.upper(), logging.INFO)
except AttributeError:
    log_level_value = logging.INFO

logging.basicConfig(
    level=log_level_value,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
)

# 确保 uvicorn 的日志级别与应用一致
logging.getLogger("uvicorn.access").setLevel(log_level_value)
logging.getLogger("uvicorn.error").setLevel(log_level_value)

# 挂载整个目录，支持 index.html 自动路由
BASE_DIR = p_pathlib(__file__).resolve().parent
# 支持的图片扩展名（可按需增减）
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}


if not os.path.exists("Dress") and minimum_mode != "true":
    logging.info("未在当前目录发现Dress仓库，将以最小化API运行")
    minimum_mode = "true"
    try:
        index_id = asyncio.run(get_github_index())
        index_author = asyncio.run(get_github_index("index_1.json"))
    except Exception as e:
        logging.error(f"获取远端数据失败: {e}")
        raise RuntimeError("无法连接到远程服务器获取数据")
elif minimum_mode == "true":
    # 即使存在Dress目录，如果用户强制设置为最小化模式，也要使用远程数据
    logging.info("强制使用最小化API运行模式")
    try:
        index_id = asyncio.run(get_github_index())
        index_author = asyncio.run(get_github_index())
    except Exception as e:
        logging.error(f"获取远端数据失败: {e}")
        raise RuntimeError("无法连接到远程服务器获取数据")
else:
    # 在非最小化模式下，也需要初始化data变量，以防万一需要使用
    data = None


@asynccontextmanager
async def auto_sync_on_start(app: FastAPI):
    # 启动自动同步任务
    if auto_sync_enabled == "true":
        logging.info(f"启动自动同步任务,同步间隔{auto_sync_time}秒")
        sync_task = asyncio.create_task(auto_sync())
        try:
            yield
        finally:
            sync_task.cancel()
    else:
        yield


app = FastAPI(
    title="Dress-API：面向可爱男孩子的一个API",
    terms_of_service="https://creativecommons.org/licenses/by-nc-sa/4.0/",
    description="“本服务所使用的图片来自 [Cute-Dress/Dress](https://github.com/Cute-Dress/Dress)，遵循 CC BY-NC-SA 4.0 许可。”",
    lifespan=auto_sync_on_start,  # 添加生命周期管理器
)
app.add_middleware(CORSMiddleware, allow_origins=["*"])


async def auto_sync():
    """
    启动时自动同步 Dress 仓库（仅非最小化模式）
    """
    global index_author, index_id, jsdelivr_ok, github_ok
    if auto_sync_enabled == "true":
        while True:
            async with httpx.AsyncClient() as client:
                # Check GitHub
                try:
                    resp = await client.get("https://github.com", timeout=10.0)
                    github_ok = resp.status_code == 200
                except httpx.RequestError:
                    github_ok = False

                # Check jsDelivr
                jsdelivr_ok = False
                jsdelivr_urls = [
                    "https://cdn.jsdelivr.net/",
                    "https://fastly.jsdelivr.net/",
                    "https://gcore.jsdelivr.net/",
                    "https://testingcf.jsdelivr.net/",
                ]
                for url in jsdelivr_urls:
                    try:
                        resp = await client.get(url, timeout=10.0)
                        if resp.status_code in (200, 301):
                            jsdelivr_ok = True
                            break
                    except httpx.RequestError:
                        continue  # Try next URL
            # 使用无限循环替代单次sleep

            if minimum_mode != "true":
                logging.info("开始执行本地Dress仓库同步...")
                await asyncio.to_thread(run_git_pull)  # run_git_pull 不是异步函数
                if force_remote_index == "true":
                    index_id = await get_github_index("index_0.json")
                    index_author = await get_github_index("index_1.json")
                    with open("public/index_0.json", "w", encoding="utf-8") as f:
                        json.dump(index_id, f, ensure_ascii=False, indent=4)
                        logging.info("作者索引已写入")
                    with open("public/index_1.json", "w", encoding="utf-8") as f:
                        json.dump(index_author, f, ensure_ascii=False, indent=4)
                        logging.info("id索引已写入")
                else:
                    try:
                        repo = Repo("Dress")
                        index = build_index_by_author(repo)
                        index_author = index

                        index_id = convert_index_author_to_index_id(index)
                        with open("public/index_1.json", "w", encoding="utf-8") as f:
                            json.dump(index_author, f, ensure_ascii=False, indent=4)
                        with open("public/index_0.json", "w", encoding="utf-8") as f:
                            json.dump(index_id, f, ensure_ascii=False, indent=4)
                        logging.debug("本地Dress仓库同步完成")
                    except FileNotFoundError as e:
                        logging.error(f"Dress目录不存在: {e}")
                    except PermissionError as e:
                        logging.error(f"权限不足: {e}")
                    except Exception as e:
                        logging.error(f"自动同步时构建索引失败: {e}")
            else:
                logging.debug("开始执行远程数据同步...")
                try:
                    index_id = await get_github_index(index="index_0.json")
                    index_author = await get_github_index(index="index_1.json")
                    with open("public/index_0.json", "w", encoding="utf-8") as f:
                        json.dump(index_id, f, ensure_ascii=False, indent=4)
                    with open("public/index_1.json", "w", encoding="utf-8") as f:
                        json.dump(index_author, f, ensure_ascii=False, indent=4)
                    logging.debug(f"已从GitHub获取最新数据，共{len(index_id)}项数据)")
                except Exception as e:
                    logging.error(f"远程数据同步失败: {e}")
            await asyncio.sleep(auto_sync_time)  # 每10秒同步一次，便于观察
    else:
        async with httpx.AsyncClient() as client:
            # Check GitHub
            try:
                resp = await client.get("https://github.com", timeout=10.0)
                github_ok = resp.status_code == 200
            except httpx.RequestError:
                github_ok = False

            # Check jsDelivr
            jsdelivr_ok = False
            jsdelivr_urls = [
                "https://cdn.jsdelivr.net/",
                "https://fastly.jsdelivr.net/",
                "https://gcore.jsdelivr.net/",
                "https://testingcf.jsdelivr.net/",
            ]
            for url in jsdelivr_urls:
                try:
                    resp = await client.get(url, timeout=10.0)
                    if resp.status_code in (200, 301):
                        jsdelivr_ok = True
                        break
                except httpx.RequestError:
                    continue  # Try next URL
        pass


async def run_one_sync():
    global index_author, index_id, jsdelivr_ok, github_ok
    async with httpx.AsyncClient() as client:
        # Check GitHub
        try:
            resp = await client.get("https://github.com", timeout=10.0)
            github_ok = resp.status_code == 200
        except httpx.RequestError:
            github_ok = False

        # Check jsDelivr
        jsdelivr_ok = False
        jsdelivr_urls = [
            "https://cdn.jsdelivr.net/",
            "https://fastly.jsdelivr.net/",
            "https://gcore.jsdelivr.net/",
            "https://testingcf.jsdelivr.net/",
        ]
        for url in jsdelivr_urls:
            try:
                resp = await client.get(url, timeout=10.0)
                if resp.status_code in (200, 301):
                    jsdelivr_ok = True
                    break
            except httpx.RequestError:
                continue  # Try next URL
    # 使用无限循环替代单次sleep

    if minimum_mode != "true":
        logging.info("开始执行本地Dress仓库同步...")
        await asyncio.to_thread(run_git_pull)  # run_git_pull 不是异步函数
        if force_remote_index == "true":
            index_id = await get_github_index("index_0.json")
            index_author = await get_github_index("index_1.json")
            with open("public/index_0.json", "w", encoding="utf-8") as f:
                json.dump(index_id, f, ensure_ascii=False, indent=4)
            with open("public/index_1.json", "w", encoding="utf-8") as f:
                json.dump(index_author, f, ensure_ascii=False, indent=4)
        else:
            try:
                repo = Repo("Dress")
                index = build_index_by_author(repo)
                index_author = index

                index_id = convert_index_author_to_index_id(index)
                with open("public/index_1.json", "w", encoding="utf-8") as f:
                    json.dump(index_author, f, ensure_ascii=False, indent=4)
                with open("public/index_0.json", "w", encoding="utf-8") as f:
                    json.dump(index_id, f, ensure_ascii=False, indent=4)
                logging.debug("本地Dress仓库同步完成")
            except FileNotFoundError as e:
                logging.error(f"Dress目录不存在: {e}")
            except PermissionError as e:
                logging.error(f"权限不足: {e}")
            except Exception as e:
                logging.error(f"自动同步时构建索引失败: {e}")
    else:
        logging.debug("开始执行远程数据同步...")
        try:
            index_id = await get_github_index(index="index_0.json")
            index_author = await get_github_index(index="index_1.json")
            with open("public/index_0.json", "w", encoding="utf-8") as f:
                json.dump(index_id, f, ensure_ascii=False, indent=4)
            with open("public/index_1.json", "w", encoding="utf-8") as f:
                json.dump(index_author, f, ensure_ascii=False, indent=4)
            logging.debug(f"已从GitHub获取最新数据，共{len(index_id)}项数据)")
        except Exception as e:
            logging.error(f"远程数据同步失败: {e}")  # 每10秒同步一次，便于观察


@app.get("/v1/dress", summary="获取一张可爱男孩子的自拍")
@app.post("/v1/dress", summary="获取一张可爱男孩子的自拍")
async def random_setu(request: Request,
                      num: int = Query(1, description="可选，指定返回数量，默认为1"),
                      author: str = Query(None, description="可选，指定作者名称以获取该作者的图片"),):
    """
    你 GET 一下就行了
    参数放url
    POST也行，参数放在 body 里，json格式，num 和 author 都是可选的，例如：
    {"num": 3, "author": "nekozzx"}
    """
    # 检查是否为 POST 请求，如果是，则从请求体获取参数
    if request.method == "POST":
        try:
            body = await request.json()
            num = body.get("num", num)
            author = body.get("author", author)
            if isinstance(author, str):
                author = [author]  # 如果是单个字符串，转换为列表
        except Exception:
            pass
    elif request.method == "GET":
        if author:
            author = author.split("|")
        else:
            pass
    else:
        raise HTTPException(status_code=405, detail="Method Not Allowed")

    base_url = request.base_url
    global index_id,index_author

    max_count = len(index_id.keys())
    if max_count == 0:
        # 立即尝试读本地索引
        try:
            with open("public/index_0.json", "r", encoding="utf-8") as f:
                index_id = json.load(f)
                max_count = len(index_id.keys())
            with open("public/index_1.json", "r", encoding="utf-8") as f:
                index_author = json.load(f)
        except:
        # 本地索引读失败立即开始一次同步
            await run_one_sync()
    
    # 确保num不超过最大值
    num = min(num, max_count)
    author_all_count = 0 
    results = []
    used_paths = set()  # 用于存储已使用的path，确保不重复
    if minimum_mode == "true":
        img_base_url = "https://testingcf.jsdelivr.net/gh/Cute-Dress/Dress@master/"
    else:
        img_base_url = f"{base_url}img/"
    if author:
        
        for one_author in author:
            if one_author in index_author:
                author_all_count += len(index_author[one_author]["contribution"])
            else:
                raise HTTPException(status_code=404, detail=f"Author {one_author} Not Found")
        num = min(num, author_all_count)
        while len(results) < num:
            now_author = random.choice(author)
            entry = await random_pick_author(index_author, img_base_url, now_author)
            if entry["url"] not in used_paths:
                used_paths.add(entry["url"])
                results.append(entry)
            else:
                continue
    else:
        # 随机选择num个不同的图片
        while len(results) < num:
            entry = await random_pick(index_id, img_base_url)
            if entry["url"] not in used_paths:
                used_paths.add(entry["url"])
                results.append(entry)
            else:
                continue
    # 如果只请求一个，返回单个对象，保持向后兼容
    if num == 1 and results:
        return results[0]
    return results


@app.post("/v1/dress/sync", summary="同步远程 Dress 仓库")
async def sync_dress_repo(
    request: Request,
    background_tasks: BackgroundTasks,
    rebuild_index: bool = Query(...),  # 默认重建索引
    x_api_key: str = Header(None, alias="X-API-Key"),  # 必须提供 Header
):
    # 检查是否为 POST 请求，如果是，则从请求体获取参数
    if request.method == "POST":
        try:
            body = await request.json()
            rebuild_index = body.get("rebuild_index", rebuild_index)
        except Exception:
            pass
    """
    触发服务器拉取 Dress 仓库的最新提交，并重建索引
    """
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    asyncio.create_task(run_one_sync())
    return {"code": 200, "message": "Sync started in background,please wait..."}


# 克隆仓库


@app.get("/v1/health", summary="健康检查")
async def health_check():

    return {
        "status": "healthy",
        "minimum_mode": minimum_mode,
        "auto_sync_enabled": auto_sync_enabled,
        "auto_sync_time": auto_sync_time,
        "connectivity_to_gitHub": github_ok,
        "connectivity_to_jsdelivr": jsdelivr_ok,
    }


@app.get("/v1/dress/index/{name}", summary="获取指定索引文件内容")
@app.post("/v1/dress/index/{name}", summary="获取指定索引文件内容")
async def return_index(
    name: Annotated[
        str, Path(description="索引名称，支持 index_0.json 和 index_1.json")
    ],
):
    """
    获取指定索引文件内容
    """
    if name not in ["index_0.json", "index_1.json"]:
        raise HTTPException(status_code=400, detail="Invalid index name")
    try:
        with open(f"public/{name}", "r", encoding="utf-8") as f:
            index_data = json.load(f)
        return index_data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Index file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Index file is corrupted")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading index file: {e}")


@app.get("/v1/dress/author/{author}", summary="获取指定作者的图片信息")
@app.post("/v1/dress/author/{author}", summary="获取指定作者的图片信息")
async def return_author_info(author: Annotated[str, Path(description="作者名称")]):
    """
    获取指定作者的图片信息
    """
    try:
        global index_author
        if len(index_author) == 0:  # 索引为空时立即尝试读本地索引
            try:
                with open("public/index_1.json", "r", encoding="utf-8") as f:
                    index_author = json.load(f)
            except Exception as e:
                logging.warning(f"本地作者索引文件读取失败: {e}")
                # 立即开始一次同步
                await run_one_sync()

        author_data = index_author[author]
        return {author: author_data}
    except KeyError:
        raise HTTPException(status_code=404, detail="Author not found")

@app.get("/i/love/you",include_in_schema=False)
async def love_you(response: Response):
    which = random.randint(0, 1)
    if which == 0:
        response.status_code = 520
        return "I love you too!Please don't forget me!"
    else:
        response.status_code = status.HTTP_418_IM_A_TEAPOT
        return 'I am a teapot!!!!!'
    
if minimum_mode != "true":
    app.mount("/img", StaticFiles(directory=BASE_DIR / "Dress"), name="static")
app.mount("/", StaticFiles(directory=BASE_DIR / "public", html=True), name="static")
if __name__ == "__main__":
    colorama.init(autoreset=True)
    print(f"🚀 启动服务: http://0.0.0.0:{ports}")
    print(
        Fore.LIGHTBLUE_EX
        + """
██████╗ ██████╗ ███████╗███████╗███████╗       █████╗ ██████╗ ██╗
██╔══██╗██╔══██╗██╔════╝██╔════╝██╔════╝      ██╔══██╗██╔══██╗██║
██║  ██║██████╔╝█████╗  ███████╗███████╗█████╗███████║██████╔╝██║
██║  ██║██╔══██╗██╔══╝  ╚════██║╚════██║╚════╝██╔══██║██╔═══╝ ██║
██████╔╝██║  ██║███████╗███████╗███████╗      ██║  ██║██║     ██║
╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝      ╚═╝  ╚═╝╚═╝     ╚═╝
    Attribution-NonCommercial-ShareAlike 4.0 International
                GitHub:Cute-Dress/Dress
            GitHub(Dress-api):nomdn/dress-api                                    
    """
    )
    print(Style.RESET_ALL + "")

    # 创建事件循环并同时运行自动同步和web服务器

    # 启动web服务器
    uvicorn.run(app, host="0.0.0.0", port=ports, log_level=log_level.lower())
