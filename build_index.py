import json
from pathlib import Path
from git import Repo
from dress_tools import build_index, build_index_by_author, escape_hash_in_index
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
                    )
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
    index_0 = build_index(repo)
    index_0 = escape_hash_in_index(index_0, "url")
    with open(out_dir / "index_0.json", "w", encoding="utf-8") as f:
        json.dump(index_0, f, ensure_ascii=False, indent=4)


    # 构建作者索引
    index_1 = build_index_by_author(repo)
    index_1 = escape_hash_in_index(index_1, "author")
    with open(out_dir / "index_1.json", "w", encoding="utf-8") as f:
        json.dump(index_1, f, ensure_ascii=False, indent=4)

    print(f"✅ 索引已生成并保存至: {out_dir.absolute()}")
if __name__ == "__main__":
    build_and_save_indexes(repo_path="./Dress", output_dir="public")