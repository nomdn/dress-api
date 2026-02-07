import json
from pathlib import Path
import sys
from git import Repo
from tqdm import tqdm
import colorama
from dress_tools import escape_hash_in_index,build_index,convert_index_id_to_index_author
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
                    )
async def build_and_save_indexes(repo_path: str, output_dir: str = "public"):
    """
    主入口函数：自动构建并保存 index_0.json 和 index_1.json
    :param repo_path: Dress 仓库本地路径（如 "./Dress"）
    :param output_dir: 输出目录（默认 "public"）
    """
    dress_dir = Path(repo_path).resolve()
    repo = Repo(repo_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(exist_ok=True)

    # 使用组合函数一次性构建两个索引，避免重复的文件遍历
    index_0 = await build_index(repo)
    index_1 = await convert_index_id_to_index_author(index_0)
    index_0 = escape_hash_in_index(index_0, "url")
    index_1 = escape_hash_in_index(index_1, "author")
    with open(out_dir / "index_0.json", "w", encoding="utf-8") as f:
        json.dump(index_0, f, ensure_ascii=False, indent=4)

    index_1 = escape_hash_in_index(index_1, "author")
    with open(out_dir / "index_1.json", "w", encoding="utf-8") as f:
        json.dump(index_1, f, ensure_ascii=False, indent=4)

    print(f"✅ 索引已生成并保存至: {out_dir.absolute()}")
if __name__ == "__main__":
    import asyncio
    colorama.init()
    asyncio.run(build_and_save_indexes(repo_path="./Dress", output_dir="public"))