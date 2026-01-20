import json
from pathlib import Path
from git import Repo

# 支持的图片扩展名（可按需增减）
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}


def normalize_url(path: str) -> str:
    """
    将文件路径中的 '#' 替换为 URL 安全的 '%23'
    注意：输入应为相对路径字符串（如 "#/a.jpg"）
    """
    return path.replace("#", "%23")


def get_all_committers(repo, file_path):
    """
    获取指定文件所有历史提交的作者（去重）
    :param repo: git.Repo 实例
    :param file_path: 相对于仓库根目录的文件路径（如 "folder/image.jpg"）
    :return: list of (name, email)
    """
    authors = set()
    for commit in repo.iter_commits(paths=file_path):
        authors.add((commit.author.name, commit.author.email))
    return list(authors)


def get_dress_image_paths(dress_dir: Path):
    """
    递归扫描 Dress 目录，返回所有支持图片的 POSIX 风格相对路径列表
    :param dress_dir: Path 对象，指向本地 Dress 仓库根目录
    :return: sorted list of str (e.g., ["a.jpg", "sub/b.png"])
    """
    if not dress_dir.exists():
        raise FileNotFoundError(f"Dress 目录不存在: {dress_dir}")

    image_paths = []
    for file_path in dress_dir.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS:
            real_path = file_path.relative_to(dress_dir)
            posix_path = real_path.as_posix()  # 统一为 / 分隔
            image_paths.append(posix_path)

    return sorted(image_paths)


def build_index(repo, dress_dir: Path):
    """
    构建主索引：{id: [path, [(author, email), ...]]}
    :param repo: git.Repo 实例
    :param dress_dir: Dress 仓库路径
    :return: dict
    """
    index = {}
    paths = get_dress_image_paths(dress_dir)
    print(f"共找到 {len(paths)} 张图片用于构建主索引")
    for idx, path in enumerate(paths, start=1):
        uploader_data = get_all_committers(repo, path)
        index[idx] = [path, uploader_data]
    return index


def build_index_by_author(repo, dress_dir: Path):
    """
    构建作者索引：{author_name: [path1, path2, ...]}
    使用首次提交者作为作者代表
    :param repo: git.Repo 实例
    :param dress_dir: Dress 仓库路径
    :return: dict
    """
    index_by_author = {}
    paths = get_dress_image_paths(dress_dir)
    print(f"共找到 {len(paths)} 张图片用于构建作者索引")
    for path in paths:
        uploader_data = get_all_committers(repo, path)
        if not uploader_data:
            print(f"⚠️ 警告: {path} 无提交记录，跳过")
            continue
        author_name = uploader_data[0][0]  # 首次提交者
        if author_name not in index_by_author:
            index_by_author[author_name] = []
        index_by_author[author_name].append(path)
    return index_by_author


def escape_hash_in_index(index_data, index_type):
    """
    对索引中的路径进行 URL 安全转义（# → %23）
    - index_type="url":   处理 {id: [path, uploader]}
    - index_type="author": 处理 {author: [path1, path2, ...]}
    """
    if not isinstance(index_data, dict):
        raise TypeError("输入必须是字典")

    if index_type == "url":
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
        raise ValueError(f"不支持的索引类型: {index_type}")


def build_and_save_indexes(repo_path: str, output_dir: str = "public"):
    """
    主入口函数：自动构建并保存 index_0.json 和 index_1.json
    :param repo_path: Dress 仓库本地路径（如 "./Dress"）
    :param output_dir: 输出目录（默认 "public"）
    """
    dress_dir = Path(repo_path).resolve()
    repo = Repo(repo_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(exist_ok=True)

    # 构建主索引
    index_0 = build_index(repo, dress_dir)
    index_0 = escape_hash_in_index(index_0, "url")
    with open(out_dir / "index_0.json", "w", encoding="utf-8") as f:
        json.dump(index_0, f, ensure_ascii=False, indent=4)


    # 构建作者索引
    index_1 = build_index_by_author(repo, dress_dir)
    index_1 = escape_hash_in_index(index_1, "author")
    with open(out_dir / "index_1.json", "w", encoding="utf-8") as f:
        json.dump(index_1, f, ensure_ascii=False, indent=4)

    print(f"✅ 索引已生成并保存至: {out_dir.absolute()}")
if __name__ == "__main__":
    build_and_save_indexes(repo_path="Dress")