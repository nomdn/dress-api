import json
import os
import subprocess
import logging
import httpx
from os import name
from pathlib import Path

from git import Repo
from typing import List, Tuple

# 禁用httpx的DEBUG日志，避免网络请求产生过多调试信息
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
                    )
def get_all_file_path(path: str) -> Tuple[List[str], List[str]]:
    """
    获取目录下的所有图片和 README 文件路径

    Returns:
        Tuple[List[str], List[str]]: (图片相对路径列表，README 相对路径列表)
        路径格式：相对于 path 目录的 POSIX 风格字符串
    """
    p = Path(path).resolve()
    img_paths = []
    readme_paths = []

    # 统一用小写匹配（兼容 Windows/Linux）
    IMG_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    README_NAMES = {"readme", "readme.md", "readme.txt", "readme.rst"}

    for files in p.rglob("*"):
        try:
            if not files.is_file():
                continue

            # 计算相对路径（关键！）
            relative_path = files.relative_to(p)
            # 转换为 POSIX 风格（/ 分隔符）
            posix_path = relative_path.as_posix()

            # 小写后缀匹配
            suffix_lower = files.suffix.lower()
            name_lower = files.name.lower()

            if suffix_lower in IMG_EXTENSIONS:
                img_paths.append(posix_path)

            if name_lower in README_NAMES:
                readme_paths.append(posix_path)

        except Exception as e:
            logging.warning(f"处理文件 {files} 时出错：{e}")
            continue
    img_paths.sort()
    readme_paths.sort()

    logging.info(f"扫描完成：{len(img_paths)} 张图片，{len(readme_paths)} 个 README")
    return img_paths, readme_paths


import asyncio
from git import Repo
from typing import List


async def _run_git_log_follow(repo: Repo, file_path: str) -> List[List[str]]:
    """
    执行 git log --follow --format="%H|%an|%ae|%cI" -- <file>
    使用 repo.working_dir 作为 cwd
    返回 [[commit_hash, author_name, author_email, committed_iso_time], ...]
    """
    try:
        # ✅ 使用异步 subprocess
        proc = await asyncio.create_subprocess_exec(
            "git", "log", "--follow", "-M100%",
            "--format=%H|%an|%ae|%cI",
            "--", file_path,
            cwd=repo.working_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # 等待完成，带超时
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=30
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            logging.error(f"git log 超时 ({file_path})")
            return []

        if proc.returncode != 0:
            logging.debug(f"git log --follow failed for {file_path}: {stderr.decode()}")
            return []

        lines = []
        for line in stdout.decode('utf-8').strip().split('\n'):
            if line and '|' in line:
                parts = line.split('|', 3)
                if len(parts) == 4:
                    lines.append(parts)
        return lines

    except Exception as e:
        logging.error(f"执行 git log --follow 出错 ({file_path}): {e}")
        return []
async def build_index_by_author(repo:Repo):
    working_path = repo.working_dir
    index_author = {}
    token = os.getenv("GITHUB_TOKEN")
    img_paths,readme_paths = get_all_file_path(working_path)
    for i in img_paths:
        author_lists = await _run_git_log_follow(repo,i)
        first_author_info = author_lists[-1]
        first_author_commit_hash = first_author_info[0]
        first_author_name = first_author_info[1]
        first_author_email = first_author_info[2]
        first_upload_time = str(first_author_info[3])
        logging.debug(f"处理文件{i}，第一提交者{first_author_info}")
        if first_author_name not in index_author.keys():
            index_author[first_author_name] = {
                "email":first_author_email,
                "contribution":[
                    {
                        "hash":first_author_commit_hash,
                        "path":i,
                        "time":first_upload_time
                    }
                ]
            }
        else:
            index_author[first_author_name]["contribution"].append({"path":i,"time":first_upload_time,"hash":first_author_commit_hash})
    for i in readme_paths:
        author_lists = await _run_git_log_follow(repo, i)
        first_author_info=author_lists[-1]
        first_author_name=first_author_info[1]
        if first_author_name not in index_author.keys():
            continue
        if "readme" not in index_author[first_author_name]:
            index_author[first_author_name]["readme"] = []
        index_author[first_author_name]["readme"].append(i)
    async with httpx.AsyncClient() as client:
        for author in index_author.keys():

            for i in range(10):
                try:
                    headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}"}
                    result = await client.get(f"https://api.github.com/users/{author}", headers=headers, timeout=10)
                    if result.status_code == 404:
                        logging.warning(f"开发者{author},在 GitHub 上的账号无法查询")
                        logging.info("通过 commit hash 反推作者中")
                        try:
                            headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}"}
                            commit_result = await client.get(
                                f'https://api.github.com/repos/Cute-Dress/Dress/commits/{index_author[author]["contribution"][0]["hash"]}',
                                headers=headers, timeout=10)
                            if commit_result.status_code == 403:
                                logging.warning("您的IP或访问密钥已被Github限流")
                                index_author[author]["avatar_url"] = None
                                index_author[author]["github_username"] = None
                                break
                            if commit_result.status_code == 404:
                                logging.warning("无法溯源到原作者的任何信息")
                                index_author[author]["avatar_url"] = None
                                index_author[author]["github_username"] = None
                                break
                            commit_data = commit_result.json()

                            author_info = commit_data.get("author")
                            if author_info:
                                index_author[author]["avatar_url"] = author_info.get("avatar_url", "") + "?size=500"
                                index_author[author]["github_username"] = author_info.get("login")
                                logging.debug(f"{author_info['login']}已找到！")
                            else:
                                index_author[author]["avatar_url"] = None
                                index_author[author]["github_username"] = None
                        except Exception as e:
                            logging.warning(f"发生错误:{e}")
                            index_author[author]["avatar_url"] = None
                            index_author[author]["github_username"] = None

                        break
                    if result.status_code == 403:
                        logging.warning("您的IP或访问密钥已被Github限流")
                        index_author[author]["avatar_url"] = None
                        index_author[author]["github_username"] = None
                        break
                    result_data = result.json()
                    avatar_url = result_data.get("avatar_url", "")
                    if avatar_url:
                        index_author[author]["avatar_url"] = avatar_url + "?size=500"
                        index_author[author]["github_username"] = result_data.get("login")
                    break
                except Exception as e:
                    logging.warning(f"发生错误:{e}")
                    index_author[author]["avatar_url"] = None
                    index_author[author]["github_username"] = None
    logging.info("处理重复贡献者中...")

    # 用于记录要删除的 git 用户名（字典的 key）
    authors_to_delete = set()

    # 转为列表遍历（避免遍历字典时修改）
    author_items = list(index_author.items())

    for i, (git_username, author) in enumerate(author_items):
        if not author or not isinstance(author, dict):
            continue

        author_github = author.get("github_username")
        if not author_github:
            continue

        # 跳过已被标记删除的
        if git_username in authors_to_delete:
            continue

        for j, (another_git_username, another_author) in enumerate(author_items):
            if i == j:
                continue  # 跳过自己

            if not another_author or not isinstance(another_author, dict):
                continue

            # 跳过已被标记删除的
            if another_git_username in authors_to_delete:
                continue

            another_github = another_author.get("github_username")
            if not another_github:
                continue

            if author_github == another_github:
                # 合并贡献列表
                for item in another_author.get("contribution", []):
                    if item and item.get("path"):
                        author["contribution"].append(item)
                if another_author.get("readme"):
                    if "readme" not in author:
                        author["readme"] = []
                    author["readme"].extend(another_author["readme"])
                # 标记为待删除（记录 git 用户名 key）
                authors_to_delete.add(another_git_username)
                logging.debug(f"标记删除: {another_git_username} (合并到 {git_username})")

    # 真正从字典中删除
    for git_username in authors_to_delete:
        if git_username in index_author:
            del index_author[git_username]
            logging.debug(f"已删除: {git_username}")

    logging.info(f"合并完成: 删除 {len(authors_to_delete)} 个重复作者")

    # 最后清洗：去重、过滤 null
    for author in index_author.values():
        if not author or not isinstance(author, dict):
            continue

        seen_paths = set()
        clean_list = []
        for item in author.get("contribution", []):
            if item is None:
                continue
            path = item.get("path")
            if not path or path in seen_paths:
                continue
            seen_paths.add(path)
            clean_list.append(item)
        author["contribution"] = clean_list

        if author.get("readme"):
            author["readme"] = list(dict.fromkeys(author["readme"]))
    logging.info("处理 URL 编码...")
    for author, data in index_author.items():  # ✅ 修复：正确遍历
        for url in data.get("contribution", []):
            url["path"] = url["path"].replace("#", "%23")
        if data.get("readme"):
            data["readme"] = [p.replace("#", "%23") for p in data["readme"]]



    return index_author
async def convert_index_author_to_index_id(index_author: dict) -> dict:
    index_id ={}
    id = 0
    for authors in index_author.keys():
        for contribution in index_author[authors]["contribution"]:
            logging.debug(f"处理{contribution},ID为{id}")
            contribution["author"]=authors
            index_id[id] = contribution
            id+=1
    return index_id




if __name__ == "__main__":
    repo=Repo("Dress")
    index_author=asyncio.run(build_index_by_author(repo))
    with open("public/index_1.json","w",encoding="utf-8") as f:
        json.dump(index_author,f,ensure_ascii=False,indent=4)
    index_id = asyncio.run(convert_index_author_to_index_id(index_author))
    with open("public/index_0.json","w",encoding="utf-8") as f:
        json.dump(index_id,f,ensure_ascii=False, indent=4)