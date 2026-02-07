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
from fastapi import FastAPI, Response, Request, BackgroundTasks, HTTPException, Header, Query,Path
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from urllib.parse import urljoin, urlparse
from httpx import TimeoutException
from contextlib import asynccontextmanager  # 添加这个导入
from dress_tools import (
    build_index,
    build_index_by_author,
    convert_index_id_to_index_author,
    escape_hash_in_index,
    normalize_url,
    get_all_committers,
    get_dress_image_paths,
    run_git_pull,
    get_github_index
)

API_KEY = "admin"
ports = 8092
log_level = "INFO"
auto_sync_enabled = "true"
auto_sync_time = 86400  # 默认24小时
minimum_mode = "false"
http_client = httpx.AsyncClient()
if os.environ.get("ARK_API_KEY") and os.environ.get("PORTS") and os.environ.get("LOG_LEVEL") and os.environ.get("AUTO_SYNC") and os.environ.get("AUTO_SYNC_TIME") and os.environ.get("FORCE_MINING"):
    API_KEY = os.environ.get("ARK_API_KEY")
    ports = int(os.environ.get("PORTS"))  # 确保转换为整数
    log_level = os.environ.get("LOG_LEVEL")
    auto_sync_enabled = os.environ.get("AUTO_SYNC")
    auto_sync_time = int(os.environ.get("AUTO_SYNC_TIME"))  # 确保转换为整数
    minimum_mode = os.environ.get("FORCE_MINING")
    
elif os.path.exists(".env"):
    load_dotenv()  # 先加载 .env（如果存在）
    # 加载 .env 后，使用默认值或环境变量值
    API_KEY = os.environ.get("ARK_API_KEY") or API_KEY
    ports = int(os.environ.get("PORTS") or ports)  # 确保转换为整数
    log_level = os.environ.get("LOG_LEVEL") or log_level
    auto_sync_enabled = os.environ.get("AUTO_SYNC") or auto_sync_enabled
    auto_sync_time = int(os.environ.get("AUTO_SYNC_TIME") or auto_sync_time)  # 确保转换为整数
    minimum_mode = os.environ.get("FORCE_MINING") or minimum_mode  # 确保从 .env 加载的值被使用

else:
    if os.path.exists("/.dockerenv"):
        raise RuntimeError("Docker 环境下必须通过 -e ARK_API_KEY=xxx 设置密钥")
    else:
        raise RuntimeError("请在 .env 文件中设置 ARK_API_KEY")

# 安全地设置日志级别，处理None值和无效值
if log_level is None:
    log_level = "INFO"
try:
    log_level_value = getattr(logging, log_level.upper(), logging.INFO)
except AttributeError:
    log_level_value = logging.INFO

logging.basicConfig(level=log_level_value,
                    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
                    )

# 挂载整个目录，支持 index.html 自动路由
BASE_DIR = p_pathlib(__file__).resolve().parent
# 支持的图片扩展名（可按需增减）
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}


if not os.path.exists("Dress") and minimum_mode != "true":
    logging.info("未在当前目录发现Dress仓库，将以最小化API运行")
    minimum_mode = "true"
    try:
        data = asyncio.run(get_github_index())
    except Exception as e:
        logging.error(f"获取远端数据失败: {e}")
        raise RuntimeError("无法连接到远程服务器获取数据")
elif minimum_mode == "true":
    # 即使存在Dress目录，如果用户强制设置为最小化模式，也要使用远程数据
    logging.info("强制使用最小化API运行模式")
    try:
        data = asyncio.run(get_github_index())
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
    lifespan=auto_sync_on_start  # 添加生命周期管理器
)

async def auto_sync():
    """
    启动时自动同步 Dress 仓库（仅非最小化模式）
    """
    if auto_sync_enabled != "true":
        while True: 
            # 使用无限循环替代单次sleep
            
            if minimum_mode != "true":
                logging.info("开始执行本地Dress仓库同步...")
                await asyncio.to_thread(run_git_pull)  # run_git_pull 不是异步函数
                try:
                    repo = Repo("Dress")
                    index = build_index(repo)
                    index = escape_hash_in_index(index, "url")
                    with open("public/index_0.json", "w", encoding="utf-8") as f:
                        json.dump(index, f, ensure_ascii=False, indent=4)
                    
                    index_by_author = build_index_by_author(repo)
                    index_by_author = escape_hash_in_index(index_by_author, "author")
                    with open("public/index_1.json", "w", encoding="utf-8") as f:
                        json.dump(index_by_author, f, ensure_ascii=False, indent=4)
                    logging.debug("本地Dress仓库同步完成")
                except FileNotFoundError as e:
                    logging.error(f"Dress目录不存在: {e}")
                except PermissionError as e:
                    logging.error(f"权限不足: {e}")
                except Exception as e:
                    logging.error(f"自动同步时构建索引失败: {e}")
            elif minimum_mode == "true":
                global data
                logging.debug("开始执行远程数据同步...")
                try:
                    new_data = await get_github_index(index="index_0.json")
                    data = new_data  # 确保更新全局变量
                    index_1 = await get_github_index(index="index_1.json")
                    with open("public/index_0.json", "w", encoding="utf-8") as f:
                        json.dump(new_data, f, ensure_ascii=False, indent=4)
                    with open("public/index_1.json", "w", encoding="utf-8") as f:
                        json.dump(index_1, f, ensure_ascii=False, indent=4)
                    logging.debug(f"已从GitHub获取最新数据，共{len(new_data)}项数据)")
                except Exception as e:
                    logging.error(f"远程数据同步失败: {e}")
            await asyncio.sleep(auto_sync_time)  # 每10秒同步一次，便于观察
    else:
        pass  



@app.get("/dress/v1",summary="获取一张可爱男孩子的自拍")
async def random_setu(request:Request):
    """
    你 GET 一下就行了
    """
    global data
    base_url =request.base_url
    if minimum_mode == "true":
        img_data = data
    else:
        try:
            with open("public/index_0.json","r",encoding="utf-8") as f:
                local_data = json.loads(f.read())
                img_data = local_data
        except FileNotFoundError:
            raise HTTPException(status_code=500, detail="本地索引文件不存在")
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="本地索引文件格式错误")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"读取本地索引文件时发生错误: {e}")
    
    if not img_data:
        raise HTTPException(status_code=500, detail="图片数据为空")
    
    max_count = len(img_data.keys())
    if max_count == 0:
        raise HTTPException(status_code=500, detail="图片索引为空")
    
    img_key = random.randint(a=1,b=max_count)
    entry = img_data[f"{img_key}"]
    
    img = entry[0]
    uploader_info = entry[1]
    author_names = [item[0] for item in uploader_info if item]
    
    # 检查是否存在时间信息
    upload_time = None
    if len(entry) > 2:
        upload_time = entry[2]
    
    if minimum_mode == "true":  # 修正：与"true"比较
        return {"img_url": f"https://cdn.jsdelivr.net/gh/Cute-Dress/Dress@master/{img}", "img_author": f"{author_names}",
                "upload_time": upload_time, "notice": "Cute-Dress/Dress CC-BY-NC-SA 4.0"}
    else:
        return {"img_url":f"{base_url}img/{img}","img_author":f"{author_names}","upload_time": upload_time,"notice":"Cute-Dress/Dress CC BY-NC-SA 4.0"}

@app.post("/dress/v1/sync", summary="同步远程 Dress 仓库")
async def sync_dress_repo(
    background_tasks: BackgroundTasks,
    rebuild_index: bool = Query(...),  # 默认重建索引
    x_api_key: str = Header(None, alias="X-API-Key")  # 必须提供 Header
):
    """
    触发服务器拉取 Dress 仓库的最新提交，并重建索引（可选）
    """
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    if minimum_mode == "true":
        try:
            data = await get_github_index()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取远端数据失败: {e}")
        return {
            "message": "successfully synced",
        }

    else:
        # 在后台任务中创建repo实例
        def sync_task():
            try:
                run_git_pull()
                repo = Repo("Dress")
                if rebuild_index:
                    index = build_index(repo)
                    index = escape_hash_in_index(index, "url")
                    with open("public/index_0.json", "w", encoding="utf-8") as f:
                        json.dump(index, f, ensure_ascii=False, indent=4)
                    
                    index_by_author = convert_index_id_to_index_author(index)
                    index_by_author = escape_hash_in_index(index_by_author, "author")
                    with open("public/index_1.json", "w", encoding="utf-8") as f:
                        json.dump(index_by_author, f, ensure_ascii=False, indent=4)
            except FileNotFoundError as e:
                logging.error(f"Dress目录不存在: {e}")
            except PermissionError as e:
                logging.error(f"权限不足: {e}")
            except Exception as e:
                logging.error(f"后台同步任务失败: {e}")

        background_tasks.add_task(sync_task)
        return {
            "message": "Sync started in background",
            "note": "Check server logs for result"
        }
# 克隆仓库

@app.get("/health", summary="健康检查")
async def health_check():
    connectivity_to_gitHub: bool = True
    connectivity_to_jsdelivr: bool = True
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("https://api.github.com", timeout=10.0)
            if response.status_code != 200:
                connectivity_to_gitHub = False
        except httpx.RequestError:
            connectivity_to_gitHub = False
        try:
            with httpx.AsyncClient() as client:
                for url in [
            "https://cdn.jsdelivr.net/",
            "https://fastly.jsdelivr.net/",
            "https://gcore.jsdelivr.net/",
            "https://testingcf.jsdelivr.net/"
        ]:
                    response = await client.get(url, timeout=10.0)
                    if response.status_code == 200 or response.status_code == 301:
                        break  # 只要有一个成功就行
                else:
                    connectivity_to_jsdelivr = False
            if response.status_code != 200:
                connectivity_to_jsdelivr = False
        except httpx.RequestError:
            connectivity_to_jsdelivr = False
    return {"status": "healthy", "minimum_mode": minimum_mode , "auto_sync_enabled": auto_sync_enabled,"auto_sync_time": auto_sync_time, "connectivity_to_gitHub": connectivity_to_gitHub, "connectivity_to_jsdelivr": connectivity_to_jsdelivr}

@app.get("/dress/v1/index/{name}", summary="获取指定索引文件内容")
async def return_index(
    name: Annotated[str, Path(description="索引名称，支持 index_0.json 和 index_1.json")]
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
@app.get("/dress/v1/author/{author}", summary="获取指定作者的图片信息")
async def return_author_info(author: Annotated[str, Path(description="作者名称")]):
    """
    获取指定作者的图片信息
    """
    try:
        with open(f"public/index_1.json", "r", encoding="utf-8") as f:
            index_authors_data = json.load(f)
        author_data = index_authors_data[author]
        return {author: author_data}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Author info not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Author info is corrupted")
if minimum_mode != "true":
    app.mount("/img", StaticFiles(directory=BASE_DIR / "Dress"), name="static")
app.mount("/", StaticFiles(directory=BASE_DIR / "public", html=True), name="static")
if __name__ == "__main__":

    if minimum_mode != "true":
        repo = Repo("Dress")
        print("正在检查索引...")
        try:
            if not(os.path.exists("public/index_0.json") and os.path.exists("public/index_1.json")):
                index = build_index(repo)
                index = escape_hash_in_index(index,"url")
                
                index_by_author = convert_index_id_to_index_author(index)
                index_by_author = escape_hash_in_index(index_by_author,"author")
                
                with open("public/index_0.json", "w", encoding="utf-8") as f:
                    json.dump(index,f,ensure_ascii=False,indent=4)
                with open("public/index_1.json", "w", encoding="utf-8") as f:
                    json.dump(index_by_author, f, ensure_ascii=False, indent=4)
            elif not os.path.exists("public/index_0.json"):
                index = build_index(repo)
                index = escape_hash_in_index(index,"url")
                with open("public/index_0.json", "w", encoding="utf-8") as f:
                    json.dump(index, f, ensure_ascii=False, indent=4)
            elif not os.path.exists("public/index_1.json"):
                index = build_index_by_author(repo)
                index = escape_hash_in_index(index,"author")
                with open("public/index_1.json", "w", encoding="utf-8") as f:
                    json.dump(index, f, ensure_ascii=False, indent=4)
        except FileNotFoundError as e:
            print(f"文件未找到: {e}")
            exit(1)
        except PermissionError as e:
            print(f"权限不足: {e}")
            exit(1)
        except Exception as e:
            print(f"构建索引时发生错误: {e}")
            exit(1)
    colorama.init(autoreset=True)
    print(f"🚀 启动服务: http://0.0.0.0:{ports}")
    print(Fore.LIGHTBLUE_EX+"""
██████╗ ██████╗ ███████╗███████╗███████╗       █████╗ ██████╗ ██╗
██╔══██╗██╔══██╗██╔════╝██╔════╝██╔════╝      ██╔══██╗██╔══██╗██║
██║  ██║██████╔╝█████╗  ███████╗███████╗█████╗███████║██████╔╝██║
██║  ██║██╔══██╗██╔══╝  ╚════██║╚════██║╚════╝██╔══██║██╔═══╝ ██║
██████╔╝██║  ██║███████╗███████╗███████╗      ██║  ██║██║     ██║
╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝      ╚═╝  ╚═╝╚═╝     ╚═╝
    Attribution-NonCommercial-ShareAlike 4.0 International
                GitHub:Cute-Dress/Dress
            GitHub(Dress-api):nomdn/dress-api                                    
    """)
    print(Style.RESET_ALL+"")
    
    # 创建事件循环并同时运行自动同步和web服务器

        # 启动web服务器
    uvicorn.run(app, host="0.0.0.0", port=ports)
    