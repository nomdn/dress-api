import asyncio
import sys
from tqdm import tqdm
import os
from pathlib import Path
import subprocess
import random
import json
import logging
import httpx
import colorama
from datetime import datetime
import logging
from typing import List, Tuple, Union, Optional, Dict
from colorama import Fore, Style
import uvicorn
from dotenv import load_dotenv
from git import Repo
from tqdm import trange
from tqdm.contrib.logging import logging_redirect_tqdm  

# 禁用httpx的DEBUG日志，避免网络请求产生过多调试信息
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# 配置日志

async def get_github_index(index:str="index_0.json") -> Dict:
    """获取远端 GitHub 索引数据"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=f"https://cdn.jsdelivr.net/gh/nomdn/dress-api@main/public/{index}",
                timeout=10.0
            )
        response.raise_for_status()
        data = response.json()
        return data
    except (httpx.TimeoutException, httpx.RequestError, httpx.HTTPStatusError):
        logging.warning("获取远端索引数据超时，正在重试...")
        # 修正 CDN 域名拼写（jsdelivr.net，不是 jsdeliver.net）
        for i in [
            "https://cdn.jsdelivr.net/",
            "https://fastly.jsdelivr.net/",
            "https://gcore.jsdelivr.net/",
            "https://testingcf.jsdelivr.net/"
        ]:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        url=f"{i}gh/nomdn/dress-api@main/public/{index}",
                        timeout=10.0
                    )
                response.raise_for_status()
                data = response.json()
                return data
            except (httpx.TimeoutException, httpx.RequestError, httpx.HTTPStatusError):
                continue
        else:
            raise RuntimeError("获取远端数据失败！")

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
            logging.error(f"Git pull failed: {result.stderr}")
        else:
            logging.info("Git pull succeeded")
    except subprocess.TimeoutExpired as e:
        logging.error(f"Git pull 超时: {e}")
    except subprocess.SubprocessError as e:
        logging.error(f"Git pull 子进程错误: {e}")
    except Exception as e:
        logging.error(f"Git pull 未知错误: {e}")