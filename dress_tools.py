import os
from pathlib import Path
import subprocess
import random
import json
import logging
import httpx
import colorama
from datetime import datetime

from colorama import Fore, Style
import uvicorn
from dotenv import load_dotenv
from git import Repo
from typing import List, Tuple, Dict, Union

# 配置日志


def normalize_url(path: str) -> str:
    """
    将文件路径中的 '#' 替换为 URL 安全的 '%23'
    注意：输入应为相对路径字符串（如 "#/a.jpg"）
    """
    return path.replace("#", "%23")

def get_all_committers(repo: Repo, file_path: str) -> List[Tuple[str, str]]:
    """
    获取指定文件所有历史提交的作者（去重）
    """
    main_dir = Path(__file__).parent.resolve()
    authors = set()
    try:
        for commit in repo.iter_commits(paths=file_path):
            authors.add((commit.author.name, commit.author.email))
        return list(authors)
    except Exception as e:
        logging.error(f"获取提交者信息失败: {e}")
        return []
def get_commit_time(repo: Repo, file_path: str) -> Union[datetime, None]:
    """
    获取指定文件最新版本提交时间
    
    Returns:
        datetime: 最新提交时间，失败时返回 None
    """
    try:
        for commit in repo.iter_commits(paths=file_path):
            return commit.committed_datetime
        return None
    except Exception as e:
        logging.error(f"获取提交时间失败: {e}")
        return None

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

def get_dress_image_paths(IMG_EXTENSIONS: set = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}) -> List[str]:
    # 获取当前脚本所在目录（即主程序目录）
    main_dir = Path(__file__).parent.resolve()

    # Dress 目录路径（主程序目录下的子目录）
    dress_dir = main_dir / "Dress"

    if not dress_dir.exists():
        raise FileNotFoundError(f"Dress 目录不存在: {dress_dir}")

    image_paths = []

    # 递归遍历 Dress 目录下的所有文件
    for file_path in dress_dir.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in IMG_EXTENSIONS:
            real_path = file_path.relative_to(dress_dir)
            # 强制转换为 POSIX 风格（/ 分隔），无论操作系统
            posix_path = real_path.as_posix()  # 👈 关键！
            image_paths.append(posix_path)

    return sorted(image_paths)

def build_index(repo: Repo) -> Dict[int, List]:
    """
    构建图片索引字典，键为序号，值为 [相对路径, 提交者列表, 最新提交时间]
    
    Args:
        repo (Repo): Git 仓库对象

    Returns:
        Dict[int, List]: 索引字典

    Raises:
        FileNotFoundError: 当Dress目录不存在时
        PermissionError: 当没有足够权限访问文件时
        Exception: 其他未预期的错误
    """
    index = {}

    try:
        paths = get_dress_image_paths()
        logging.info(f"共找到 {len(paths)} 张图片")

        for c, i in enumerate(paths, start=1):
            uploader_data = get_all_committers(repo, i)
            latest_commit_time = get_commit_time(repo, i)
            if not uploader_data:
                logging.warning(f"⚠️ 警告: {i} 无提交记录，跳过")
                continue
            logging.debug(f"处理图片 {c}: {i}, 上传者: {uploader_data}, 最新提交时间: {latest_commit_time}")
            # 包含时间信息
            index[c] = [i, uploader_data, latest_commit_time]

        return index

    except FileNotFoundError:
        raise
    except PermissionError:
        raise
    except Exception as e:
        logging.error(f"构建索引时发生未知错误: {e}")
        raise


def build_index_by_author(repo: Repo) -> Dict[str, List[Dict]]:
    """
    构建按作者分组的图片索引字典
    
    Args:
        repo (Repo): Git 仓库对象

    Returns:
        Dict[str, List[Dict]]: 按作者分组的索引字典，每个条目包含"path"和"latest_commit_time"

    Raises:
        FileNotFoundError: 当Dress目录不存在时
        PermissionError: 当没有足够权限访问文件时
        Exception: 其他未预期的错误
    """
    index_name = {}

    try:
        paths = get_dress_image_paths()
        logging.info(f"共找到 {len(paths)} 张图片")

        for i in paths:
            uploader_data = get_all_committers(repo, i)
            latest_commit_time = get_commit_time(repo, i)
            if not uploader_data:
                logging.warning(f"⚠️ 警告: {i} 无提交记录，跳过")
                continue
            
            author_name = uploader_data[0][0]
            logging.info(f"处理图片: {i}, 作者: {author_name}, 最新提交时间: {latest_commit_time}")
            
            if author_name not in index_name:
                index_name[author_name] = []
            # 添加包含路径和提交时间的字典到列表
            index_name[author_name].append({"path": i, "latest_commit_time": latest_commit_time})

        return index_name
        
    except FileNotFoundError:
        raise
    except PermissionError:
        raise
    except Exception as e:
        logging.error(f"构建作者索引时发生未知错误: {e}")
        raise


def escape_hash_in_index(index_data: Dict, index_type: str) -> Dict:
    """
    将路径中的 '#' 替换为 '%23'
    - index_type="url":   处理 index_0 {id: [path, uploader, latest_commit_time]}
    - index_type="author": 处理 index_1 {author: [{"path": path, "latest_commit_time": time}, ...]}
    """
    if not isinstance(index_data, dict):
        raise TypeError("输入必须是字典")
    
    result = {}
    
    if index_type == "url":
        for key, value in index_data.items():
            if isinstance(value, list) and len(value) >= 1:
                path = normalize_url(value[0])  # 处理路径中的#字符
                uploader_data = value[1]  # 提交者列表
                
                # 检查是否存在时间信息
                if len(value) > 2:
                    latest_commit_time = value[2]
                    # 如果是datetime对象，转换为ISO格式字符串
                    if hasattr(latest_commit_time, 'isoformat'):
                        latest_commit_time_str = latest_commit_time.isoformat()
                    else:
                        latest_commit_time_str = latest_commit_time
                    
                    result[key] = [path, uploader_data, latest_commit_time_str]
                else:
                    result[key] = [path, uploader_data]  # 保持原有的结构
                
    elif index_type == "author":
        for author, items in index_data.items():
            if isinstance(items, list):
                processed_items = []
                for item in items:
                    if isinstance(item, dict) and "path" in item:
                        # 如果是字典格式，处理其中的path字段，并将datetime转为字符串
                        normalized_path = normalize_url(item["path"])
                        latest_commit_time = item.get("latest_commit_time")
                        
                        # 如果是datetime对象，转换为ISO格式字符串
                        if hasattr(latest_commit_time, 'isoformat'):
                            latest_commit_time_str = latest_commit_time.isoformat()
                        else:
                            latest_commit_time_str = latest_commit_time
                        
                        processed_item = {
                            "path": normalized_path,
                            "latest_commit_time": latest_commit_time_str
                        }
                        processed_items.append(processed_item)
                    elif isinstance(item, str):
                        # 如果是字符串格式，直接处理
                        processed_items.append(normalize_url(item))
                    else:
                        # 其他情况保持原样
                        processed_items.append(item)
                result[author] = processed_items
                
    else:
        raise ValueError(f"不支持的类型: {index_type}")
        
    return result