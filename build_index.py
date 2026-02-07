import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
import httpx

# 配置
IMG_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
MAX_RETRIES = 3
BASE_DELAY = 1.0
TIMEOUT = 15.0


def _make_request_with_retry(
    client: httpx.Client,
    method: str,
    url: str,
    headers: dict,
    params: Optional[dict] = None,
    timeout: float = TIMEOUT
) -> httpx.Response:
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.request(method, url, headers=headers, params=params, timeout=timeout)
            if response.status_code < 400:
                return response
            if response.status_code == 429 or 500 <= response.status_code < 600:
                if attempt < MAX_RETRIES:
                    delay = BASE_DELAY * (2 ** attempt)
                    logging.warning(f"⚠️ {url} 返回 {response.status_code}，{delay:.1f}s 后重试")
                    time.sleep(delay)
                    continue
            return response
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            if attempt < MAX_RETRIES:
                delay = BASE_DELAY * (2 ** attempt)
                logging.warning(f"⚠️ 网络错误 ({e})，{delay:.1f}s 后重试")
                time.sleep(delay)
            else:
                raise
    raise RuntimeError("Unreachable")


def build_index_api_efficient(
    owner: str,
    repo: str,
    token: str
) -> Tuple[Dict[int, List], Dict[str, List[Dict]]]:
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    file_info: Dict[str, Dict] = {}  # path -> {first_author, all_authors, latest_time}

    # Step 1: 获取所有 commits（倒序：最新在前）
    commit_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    page = 1

    with httpx.Client() as client:
        while True:
            params = {"page": page, "per_page": 100}
            response = _make_request_with_retry(client, "GET", commit_url, headers, params, TIMEOUT)
            response.raise_for_status()
            commits = response.json()

            if not commits:
                break

            logging.info(f"处理第 {page} 页 commits（{len(commits)} 条）...")

            for commit in commits:
                sha = commit["sha"]
                author_name = commit["commit"]["author"]["name"]
                author_email = commit["commit"]["author"]["email"]
                commit_time = commit["commit"]["author"]["date"]

                # 获取该 commit 修改的文件
                try:
                    detail_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
                    detail_resp = _make_request_with_retry(client, "GET", detail_url, headers, timeout=TIMEOUT)
                    detail_resp.raise_for_status()
                    files = detail_resp.json().get("files", [])

                    for f in files:
                        path = f["filename"]
                        if Path(path).suffix.lower() in IMG_EXTENSIONS:
                            if path not in file_info:
                                # 首次出现 → 记录为 latest_time 和 first_author（后续可能被更早的覆盖）
                                file_info[path] = {
                                    "first_author": (author_name, author_email),
                                    "all_authors": set(),
                                    "latest_time": commit_time
                                }
                            file_info[path]["all_authors"].add((author_name, author_email))

                    time.sleep(0.05)

                except Exception as e:
                    logging.warning(f"跳过 commit {sha[:7]}: {e}")
                    continue

            if len(commits) < 100:
                break
            page += 1
            time.sleep(0.1)

    logging.info(f"共收集 {len(file_info)} 个图片文件的信息")

    # 构建最终索引
    index_0 = {}
    index_1: Dict[str, List[Dict]] = {}

    for idx, (path, info) in enumerate(sorted(file_info.items()), start=1):
        all_authors = list(info["all_authors"])
        latest_time = info["latest_time"]
        first_author = info["first_author"]  # 注意：这是最后一次修改者（因倒序），但对新上传文件 ≈ 首次作者

        index_0[idx] = [path, all_authors, latest_time]

        author_name = first_author[0]
        if author_name not in index_1:
            index_1[author_name] = []
        index_1[author_name].append({
            "path": path,
            "time": latest_time
        })

    return index_0, index_1


def main():
    # 从环境变量读取配置
    token = os.getenv("GH_PAT")
    owner = os.getenv("TARGET_OWNER", "Cute-Dress")
    repo = os.getenv("TARGET_REPO", "Dress")

    if not token:
        raise RuntimeError("❌ GH_PAT 环境变量未设置！请在 GitHub Actions Secrets 中配置。")

    logging.basicConfig(level=logging.INFO)

    logging.info(f"开始构建索引: {owner}/{repo}")
    index_0, index_1 = build_index_api_efficient(owner, repo, token)

    # 保存到 public 目录
    output_dir = Path("public")
    output_dir.mkdir(exist_ok=True)

    with open(output_dir / "index_0.json", "w", encoding="utf-8") as f:
        json.dump(index_0, f, ensure_ascii=False, indent=2)

    with open(output_dir / "index_1.json", "w", encoding="utf-8") as f:
        json.dump(index_1, f, ensure_ascii=False, indent=2)

    logging.info("✅ 索引构建完成并保存！")


if __name__ == "__main__":
    main()