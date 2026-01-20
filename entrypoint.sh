#!/bin/bash
set -e  # 遇错立即退出

MAX_RETRIES=5
RETRY_DELAY=3  # 秒

BASE_DIR="/app"  # 根据你的 Dockerfile 用户调整路径
# 如果你用的是 root 或 /app，请改成：
# BASE_DIR="/app"

cd "$BASE_DIR"

echo "🔍 检查 Dress 仓库是否存在..."
if [ ! -d "Dress" ]; then
    echo "📁 Dress 目录不存在，开始克隆 (分支: master)..."

    attempt=0
    while [ $attempt -lt $MAX_RETRIES ]; do
        echo "🔄 第 $((attempt + 1)) 次尝试克隆..."

        if git clone --single-branch --branch master \
                    --depth=1 \
                    https://github.com/Cute-Dress/Dress.git; then
            echo "✅ Dress 仓库克隆成功！"
            break
        else
            echo "❌ 克隆失败（尝试 $((attempt + 1))/$MAX_RETRIES）"
            attempt=$((attempt + 1))

            if [ $attempt -lt $MAX_RETRIES ]; then
                echo "⏳ 等待 ${RETRY_DELAY} 秒后重试..."
                sleep $RETRY_DELAY
            else
                echo "💥 所有重试均失败！请检查网络或 GitHub 状态。"
                exit 1
            fi
        fi
    done
else
    echo "✅ Dress 已存在，跳过克隆。"
fi

echo "🟢 启动 Python 应用..."
exec python main.py