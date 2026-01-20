import os
from pathlib import Path
import subprocess
import random
import json

import colorama
from colorama import Fore, Style
import uvicorn
from dotenv import load_dotenv
from git import Repo
import json
from fastapi import FastAPI, Response, Request, BackgroundTasks, HTTPException, Header, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from urllib.parse import urljoin, urlparse

if os.environ.get("ARK_API_KEY"):
    API_KEY = os.environ.get("ARK_API_KEY")
    ports = os.environ.get("PORTS")
elif os.path.exists(".env"):
    load_dotenv()  # 先加载 .env（如果存在）
    API_KEY = os.environ.get("ARK_API_KEY")
    ports = os.environ.get("PORTS")
else:
    if os.path.exists("/.dockerenv"):
        raise RuntimeError("Docker 环境下必须通过 -e ARK_API_KEY=xxx 设置密钥")
    else:
        raise RuntimeError("请在 .env 文件中设置 ARK_API_KEY")


# 挂载整个目录，支持 index.html 自动路由
BASE_DIR = Path(__file__).resolve().parent
# 支持的图片扩展名（可按需增减）
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
app = FastAPI(title="Dress-API：面向可爱男孩子的一个API",
              terms_of_service="https://creativecommons.org/licenses/by-nc-sa/4.0/",
              description="“本服务所使用的图片来自 Cute-Dress/Dress，遵循 CC BY-NC-SA 4.0 许可。”"
              )

def run_git_pull():
    """在后台执行 git pull"""
    try:
        result = subprocess.run(
            ["git", "pull"],
            cwd="Dress",  # 👈 替换为你的本地仓库路径
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            print(f"Git pull failed: {result.stderr}")
        else:
            print("Git pull succeeded")
    except Exception as e:
        print(f"Error during git pull: {e}")
def normalize_url(path: str) -> str:
    """
    将文件路径中的 '#' 替换为 URL 安全的 '%23'
    注意：输入应为相对路径字符串（如 "#/a.jpg"）
    """
    return path.replace("#", "%23")
def get_all_committers(repo, file_path):
    """
    获取指定文件所有历史提交的作者（去重）
    """
    main_dir = Path(__file__).parent.resolve()
    authors = set()
    for commit in repo.iter_commits(paths=file_path):
        authors.add((commit.author.name, commit.author.email))
    return list(authors)
def get_dress_image_paths():
    # 获取当前脚本所在目录（即主程序目录）
    main_dir = Path(__file__).parent.resolve()

    # Dress 目录路径（主程序目录下的子目录）
    dress_dir = main_dir / "Dress"

    if not dress_dir.exists():
        raise FileNotFoundError(f"Dress 目录不存在: {dress_dir}")

    image_paths = []

    # 递归遍历 Dress 目录下的所有文件
    for file_path in dress_dir.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS:
            real_path = file_path.relative_to(dress_dir)
            # 强制转换为 POSIX 风格（/ 分隔），无论操作系统
            posix_path = real_path.as_posix()  # 👈 关键！
            image_paths.append(posix_path)

    return sorted(image_paths)

def build_index(repo):
    index = {}
    index_name = {}

    try:
        paths = get_dress_image_paths()
        print(f"共找到 {len(paths)} 张图片：")
          # 只打印前5个示例
        for c,i in enumerate(paths,start=1):
            uploader_data = get_all_committers(repo,i)
            print(uploader_data)
            index[c] = [i,uploader_data]

        # 可选：将路径保存到文件
        # with open("image_paths.txt", "w", encoding="utf-8") as f:
        #     f.write("\n".join(paths))
        return index
    except Exception as e:
        return f"错误: {e}"
def build_index_by_author(repo):

    index_name = {}

    try:
        paths = get_dress_image_paths()
        print(f"共找到 {len(paths)} 张图片：")

          # 只打印前5个示例
        for i in paths:
            # ⚠️ 安全检查：跳过无提交记录的文件

            uploader_data = get_all_committers(repo,i)
            if not uploader_data:
                print(f"⚠️ 警告: {i} 无提交记录，跳过")
                continue
            print(uploader_data)
            if not uploader_data[0][0] in index_name.keys():
                index_name[uploader_data[0][0]] = []
                index_name[uploader_data[0][0]].append(i)
            else:
                index_name[uploader_data[0][0]].append(i)

        # 可选：将路径保存到文件
        # with open("image_paths.txt", "w", encoding="utf-8") as f:
        #     f.write("\n".join(paths))
        return index_name
    except Exception as e:
        return f"错误: {e}"


def escape_hash_in_index(index_data, index_type):
    """
    将路径中的 '#' 替换为 '%23'
    - index_type="url":   处理 index_0 {id: [path, uploader]}
    - index_type="author": 处理 index_1 {author: [path1, path2, ...]}
    """
    if not isinstance(index_data, dict):
        raise TypeError("输入必须是字典")

    if index_type == "url":
        # 构建新字典，避免副作用
        return {
            key: [normalize_url(value[0]), value[1]]
            for key, value in index_data.items()
            if isinstance(value, list) and len(value) >= 1
        }

    elif index_type == "author":
        return {
            author: [normalize_url(path) for path in paths]
            for author, paths in index_data.items()
            if isinstance(paths, list)
        }

    else:
        raise ValueError(f"不支持的类型: {index_type}")
@app.get("/dress/v1",summary="获取一张可爱男孩子的自拍")
async def random_setu(request:Request):
    """
    你 GET 一下就行了
    """
    base_url =request.base_url
    with open("public/index_0.json","r",encoding="utf-8") as f:
        data = json.loads(f.read())
    max_count = len(data.keys())
    img_key = random.randint(a=1,b=max_count)
    img= data[f"{img_key}"][0]
    author_names = [item[0] for item in data[f"{img_key}"][1] if item]
    return {"img_url":f"{base_url}img/{img}","img_author":f"{author_names}","notice":"“本服务所使用的图片来自 Cute-Dress/Dress，遵循 CC BY-NC-SA 4.0 许可。”"}
@app.post("/dresses/v1/sync", summary="同步远程 Dress 仓库")
async def sync_dress_repo(
    background_tasks: BackgroundTasks,
    rebuild_index: bool = Query(...),  # 默认重建索引
    x_api_key: str = Header(None, alias="X-API-Key")  # 必须提供 Header
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    """
    触发服务器拉取 Dress 仓库的最新提交，并重建索引（可选）
    """
    background_tasks.add_task(run_git_pull)
    if rebuild_index:
        background_tasks.add_task(build_index_by_author,repo)
        background_tasks.add_task(build_index,repo)

    return {
        "message": "Sync started in background",
        "note": "Check server logs for result"
    }

if not os.path.exists("Dress"):
    print("您还没有克隆dress仓库，正在为你克隆")
    for i in range(10):
        try:
            print(f"第 {i} 次尝试")
            subprocess.run(["git","clone","--single-branch","--branch master","https://github.com/Cute-Dress/Dress.git"], check=True, text=True, capture_output=True)
            print("克隆成功！")
            break
        except subprocess.CalledProcessError as e:
            print(f"命令执行异常！错误: {e}")
            print("开始执行重试")
        except Exception as e:
            print(f"未知错误！{e}")
            print("开始执行重试")
    else:
        raise RuntimeError("克隆仓库失败，请检查网络或 Git 配置")
app.mount("/img", StaticFiles(directory=BASE_DIR / "Dress"), name="static")
app.mount("/", StaticFiles(directory=BASE_DIR / "public", html=True), name="static")
if __name__ == "__main__":


    repo = Repo("Dress")
    print("正在检查索引...")
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
    colorama.init(autoreset=True)
    print(f"🚀 启动服务: http://0.0.0.0:{ports}")
    print(Fore.LIGHTBLUE_EX+"""
██████╗ ██████╗ ███████╗███████╗███████╗       █████╗ ██████╗ ██╗
██╔══██╗██╔══██╗██╔════╝██╔════╝██╔════╝      ██╔══██╗██╔══██╗██║
██║  ██║██████╔╝█████╗  ███████╗███████╗█████╗███████║██████╔╝██║
██║  ██║██╔══██╗██╔══╝  ╚════██║╚════██║╚════╝██╔══██║██╔═══╝ ██║
██████╔╝██║  ██║███████╗███████║███████║      ██║  ██║██║     ██║
╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝      ╚═╝  ╚═╝╚═╝     ╚═╝
    Attribution-NonCommercial-ShareAlike 4.0 International
                GitHub:Cute-Dress/Dress
                GitHub(Dress-api):nomdn/dress-api）                                       
    """)
    print(Style.RESET_ALL+"")

    uvicorn.run(app, host="0.0.0.0", port=int(ports))