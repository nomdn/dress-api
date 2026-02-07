import httpx
import time
import logging
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import json

# ======================
# 配置
# ======================
MAX_RETRIES = 3
BASE_DELAY = 1.0  # 秒
TIMEOUT = 10.0

# ======================
# 带重试的 HTTP 客户端封装
# ======================

def _make_request_with_retry(
    client: httpx.Client,
    method: str,
    url: str,
    headers: dict,
    params: Optional[dict] = None,
    timeout: float = TIMEOUT
) -> httpx.Response:
    """
    执行带重试的 HTTP 请求
    重试条件：连接错误、超时、5xx、429
    """
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                timeout=timeout
            )
            
            # 成功：2xx
            if response.status_code < 400:
                return response
            
            # 可重试错误：429 (Too Many Requests), 5xx
            if response.status_code == 429 or 500 <= response.status_code < 600:
                if attempt < MAX_RETRIES:
                    delay = BASE_DELAY * (2 ** attempt)
                    logging.warning(f"⚠️ 请求 {url} 返回 {response.status_code}，{delay}s 后重试（第 {attempt + 1} 次）")
                    time.sleep(delay)
                    continue
                else:
                    response.raise_for_status()
            else:
                # 其他 4xx 错误（如 404）不重试
                return response
                
        except (httpx.TimeoutException, httpx.ConnectError, httpx.ReadTimeout) as e:
            if attempt < MAX_RETRIES:
                delay = BASE_DELAY * (2 ** attempt)
                logging.warning(f"⚠️ 网络错误 ({e})，{delay}s 后重试（第 {attempt + 1} 次）")
                time.sleep(delay)
            else:
                raise
        except Exception:
            # 其他异常不重试
            raise
    
    raise RuntimeError("Should not reach here")

# ======================
# 辅助函数
# ======================

def normalize_url(path: str) -> str:
    return path.replace("#", "%23")

def get_all_commits_for_file(
    owner: str,
    repo: str,
    file_path: str,
    token: Optional[str] = None
) -> List[Dict]:
    """
    获取指定文件的所有 commit 历史（按时间倒序），带重试
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    all_commits = []
    page = 1
    per_page = 100
    
    with httpx.Client() as client:
        while True:
            params = {
                "path": file_path,
                "page": page,
                "per_page": per_page
            }
            try:
                response = _make_request_with_retry(client, "GET", url, headers, params, TIMEOUT)
                
                if response.status_code == 404:
                    return []  # 文件不存在
                
                response.raise_for_status()
                commits = response.json()
                if not commits:
                    break
                all_commits.extend(commits)
                if len(commits) < 100:
                    break
                page += 1
                time.sleep(0.1)
            except Exception as e:
                logging.error(f"❌ 获取 {file_path} 的 commit 彻底失败: {e}")
                break
    return all_commits

# ======================
# API 版核心函数（替代原 Git 函数）
# ======================

def api_get_all_committers(owner: str, repo: str, file_path: str, token: Optional[str] = None) -> List[Tuple[str, str]]:
    commits = get_all_commits_for_only_file(owner, repo, file_path, token)
    authors = set()
    for c in commits:
        name = c["commit"]["author"]["name"]
        email = c["commit"]["author"]["email"]
        authors.add((name, email))
    return list(authors)

def api_get_commit_time(owner: str, repo: str, file_path: str, token: Optional[str] = None) -> Optional[str]:
    commits = get_all_commits_for_only_file(owner, repo, file_path, token)
    if commits:
        return commits[0]["commit"]["author"]["date"]
    return None

def api_get_first_commit_author(owner: str, repo: str, file_path: str, token: Optional[str] = None) -> Optional[Tuple[str, str]]:
    commits = get_all_commits_for_only_file(owner, repo, file_path, token)
    if commits:
        last = commits[-1]
        return (last["commit"]["author"]["name"], last["commit"]["author"]["email"])
    return None

def get_all_commits_for_only_file(owner: str, repo: str, file_path: str, token: Optional[str] = None) -> List[Dict]:
    return get_all_commits_for_file(owner, repo, file_path, token)

# ======================
# 构建索引（纯 API 版）
# ======================

def build_index_api(
    owner: str,
    repo: str,
    token: Optional[str] = None,
    img_extensions: set = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
) -> Tuple[Dict[int, List], Dict[str, List[Dict]]]:
    image_paths = get_all_image_paths_from_github(owner, repo, token, img_extensions)
    logging.info(f"共找到 {len(image_paths)} 张图片")
    
    index_0 = {}
    index_1 = {}
    
    for idx, path in enumerate(image_paths, start=1):
        try:
            committers = api_get_all_committers(owner, repo, path, token)
            if not committers:
                logging.warning(f"⚠️ 跳过无提交记录的文件: {path}")
                continue
            
            latest_time = api_get_commit_time(owner, repo, path, token)
            first_author = api_get_first_commit_author(owner, repo, path, token)
            if not first_author:
                first_author = committers[0]
            
            # index_0
            index_0[idx] = [path, committers, latest_time]
            
            # index_1
            author_name = first_author[0]
            if author_name not in index_1:
                index_1[author_name] = []
            index_1[author_name].append({
                "path": path,
                "time": latest_time
            })
            
            if idx % 50 == 0:
                logging.info(f"已处理 {idx}/{len(image_paths)} 张图片")
            time.sleep(0.1)
            
        except Exception as e:
            logging.error(f"处理文件 {path} 时出错: {e}")
            continue  # 单个文件失败不影响整体
    
    return index_0, index_1

def get_all_image_paths_from_github(
    owner: str,
    repo: str,
    token: Optional[str] = None,
    img_extensions: set = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
) -> List[str]:
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    with httpx.Client() as client:
        # 获取默认分支
        repo_url = f"https://api.github.com/repos/{owner}/{repo}"
        resp = _make_request_with_retry(client, "GET", repo_url, headers, timeout=TIMEOUT)
        resp.raise_for_status()
        default_branch = resp.json()["default_branch"]
        
        # 获取完整 tree
        tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
        tree_resp = _make_request_with_retry(client, "GET", tree_url, headers, timeout=TIMEOUT)
        tree_resp.raise_for_status()
        tree = tree_resp.json().get("tree", [])
    
    paths = []
    for item in tree:
        if item["type"] == "blob":
            full_path = item["path"]
            if Path(full_path).suffix.lower() in img_extensions:
                paths.append(full_path)
    return paths

# ======================
# 主程序入口
# ======================

