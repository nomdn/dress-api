import os
from pathlib import Path
import subprocess
import random
import json
import httpx
import colorama
from colorama import Fore, Style
import uvicorn
import logging
from dotenv import load_dotenv
from git import Repo
import asyncio
import json
from fastapi import FastAPI, Response, Request, BackgroundTasks, HTTPException, Header, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from urllib.parse import urljoin, urlparse
from httpx import TimeoutException
from dress_tools import (
    build_index,
    build_index_by_author,
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
    ports = os.environ.get("PORTS")
    log_level = os.environ.get("LOG_LEVEL")
    auto_sync_enabled = os.environ.get("AUTO_SYNC")
    auto_sync_time = os.environ.get("AUTO_SYNC_TIME")
    minimum_mode = os.environ.get("FORCE_MINING")
    
elif os.path.exists(".env"):
    load_dotenv()  # 先加载 .env（如果存在）
    API_KEY = os.environ.get("ARK_API_KEY")
    ports = os.environ.get("PORTS")
    log_level = os.environ.get("LOG_LEVEL")
    auto_sync_enabled = os.environ.get("AUTO_SYNC")
    auto_sync_time = os.environ.get("AUTO_SYNC_TIME")
    minimum_mode = os.environ.get("FORCE_MINING")

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
BASE_DIR = Path(__file__).resolve().parent
# 支持的图片扩展名（可按需增减）
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}


if not os.path.exists("Dress"):
    logging.info("未在当前目录发现Dress仓库，将以最小化API运行")
    minimum_mode = "true"
    data=asyncio.run(get_github_index())

app = FastAPI(title="Dress-API：面向可爱男孩子的一个API",
              terms_of_service="https://creativecommons.org/licenses/by-nc-sa/4.0/",
              description="“本服务所使用的图片来自 [Cute-Dress/Dress](https://github.com/Cute-Dress/Dress)，遵循 CC BY-NC-SA 4.0 许可。”"
              )

async def auto_sync():
    """
    启动时自动同步 Dress 仓库（仅非最小化模式）
    """
    while True: 
         # 使用无限循环替代单次sleep
        if minimum_mode != "true":
            logging.info("开始执行本地Dress仓库同步...")
            await asyncio.to_thread(run_git_pull)  # run_git_pull 不是异步函数
            repo = Repo("Dress")
            try:
                index = build_index(repo)
                index = escape_hash_in_index(index, "url")
                with open("public/index_0.json", "w", encoding="utf-8") as f:
                    json.dump(index, f, ensure_ascii=False, indent=4)
                
                index_by_author = build_index_by_author(repo)
                index_by_author = escape_hash_in_index(index_by_author, "author")
                with open("public/index_1.json", "w", encoding="utf-8") as f:
                    json.dump(index_by_author, f, ensure_ascii=False, indent=4)
                logging.debug("本地Dress仓库同步完成")
            except Exception as e:
                logging.error(f"自动同步时构建索引失败: {e}")
        elif minimum_mode == "true":
            global data
            logging.debug("开始执行远程数据同步...")
            try:
                new_data = await get_github_index()
                data = new_data  # 确保更新全局变量
                logging.debug(f"已从GitHub获取最新数据，共{len(new_data)}项数据)")
            except Exception as e:
                logging.error(f"远程数据同步失败: {e}")
        await asyncio.sleep(auto_sync_time)  # 每10秒同步一次，便于观察

@app.get("/dress/v1",summary="获取一张可爱男孩子的自拍")
async def random_setu(request:Request):
    """
    你 GET 一下就行了
    """
    global data
    base_url =request.base_url
    if minimum_mode != "true":
        with open("public/index_0.json","r",encoding="utf-8") as f:
            local_data = json.loads(f.read())
            img_data = local_data
    else:

       img_data =data
    max_count = len(img_data.keys())
    img_key = random.randint(a=1,b=max_count)
    img= img_data[f"{img_key}"][0]
    author_names = [item[0] for item in img_data[f"{img_key}"][1] if item]
    upload_time = img_data[f"{img_key}"][2]
    if minimum_mode == "true":
        return {"img_url": f"https://cdn.jsdelivr.net/gh/Cute-Dress/Dress@master/{img}", "img_author": f"{author_names}",
                "upload_time": upload_time, "notice": "Cute-Dress/Dress CC-BY-NC-SA 4.0"}
    else:
        return {"img_url":f"{base_url}img/{img}","img_author":f"{author_names}","upload_time": upload_time,"notice":"Cute-Dress/Dress CC BY-NC-SA 4.0"}

@app.post("/dresses/v1/sync", summary="同步远程 Dress 仓库")
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
                    
                    index_by_author = build_index_by_author(repo)
                    index_by_author = escape_hash_in_index(index_by_author, "author")
                    with open("public/index_1.json", "w", encoding="utf-8") as f:
                        json.dump(index_by_author, f, ensure_ascii=False, indent=4)
            except Exception as e:
                logging.error(f"后台同步任务失败: {e}")

        background_tasks.add_task(sync_task)
        return {
            "message": "Sync started in background",
            "note": "Check server logs for result"
        }
# 克隆仓库


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
                
                index_by_author = build_index_by_author(repo)
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
██████╔╝██║  ██║███████╗███████╗███████║      ██║  ██║██║     ██║
╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝      ╚═╝  ╚═╝╚═╝     ╚═╝
    Attribution-NonCommercial-ShareAlike 4.0 International
                GitHub:Cute-Dress/Dress
            GitHub(Dress-api):nomdn/dress-api                                    
    """)
    print(Style.RESET_ALL+"")
    
    # 创建事件循环并同时运行自动同步和web服务器
    async def main():
        # 启动自动同步任务
        if auto_sync_enabled == "true":
            logging.info(f"启动自动同步任务,同步间隔{auto_sync_time}秒")
            sync_task = asyncio.create_task(auto_sync())
        
        # 启动web服务器
        config = uvicorn.Config(app, host="0.0.0.0", port=int(ports))
        server = uvicorn.Server(config)
        await server.serve()
    
    asyncio.run(main())