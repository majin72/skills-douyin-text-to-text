#!/bin/bash
# 自动检测并使用虚拟环境的启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"

# 检查虚拟环境是否存在
if [ ! -d "$VENV_PATH" ]; then
    echo "虚拟环境不存在，正在创建..."
    python3 "$SCRIPT_DIR/setup_venv.py" || exit 1
fi

# 获取虚拟环境中的Python路径
if [ -f "$VENV_PATH/bin/python" ]; then
    PYTHON_CMD="$VENV_PATH/bin/python"
elif [ -f "$VENV_PATH/Scripts/python.exe" ]; then
    PYTHON_CMD="$VENV_PATH/Scripts/python.exe"
else
    echo "❌ 无法找到虚拟环境中的Python"
    exit 1
fi

# 运行主脚本
exec "$PYTHON_CMD" "$SCRIPT_DIR/parse_douyin_video.py" "$@"
