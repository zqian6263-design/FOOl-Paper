#!/usr/bin/env bash
set -euo pipefail

# FOOL-paper 一键安装脚本
# 用法: bash install.sh [--dev]

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📦 安装 FOOL-paper..."
echo ""

# 检查 Python
if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
    echo "❌ 未找到 Python，请先安装 Python 3.10+"
    exit 1
fi

PYTHON=$(command -v python3 || command -v python)
PY_VERSION=$($PYTHON --version 2>&1 | grep -oP '\d+\.\d+')
echo "✅ Python: $($PYTHON --version)"

# 创建虚拟环境（如果不存在）
if [ ! -d "$REPO_DIR/.venv" ]; then
    echo "🔧 创建虚拟环境..."
    $PYTHON -m venv "$REPO_DIR/.venv"
fi

# 激活虚拟环境
source "$REPO_DIR/.venv/bin/activate" 2>/dev/null || source "$REPO_DIR/.venv/Scripts/activate" 2>/dev/null

echo "✅ 虚拟环境: $REPO_DIR/.venv"

# 安装依赖
echo "📥 安装核心依赖..."
pip install -e "$REPO_DIR"

# 开发依赖
if [ "${1:-}" = "--dev" ]; then
    echo "📥 安装开发依赖..."
    pip install -e "$REPO_DIR[dev]"
fi

echo ""
echo "🎉 FOOL-paper 安装完成!"
echo ""
echo "快速测试:"
echo "  cd $REPO_DIR"
echo '  python -c "from fool_paper import __version__; print(__version__)"'
echo ""
echo "AI Agent 入口:"
echo "  - Hermes Agent:  加载 skills/ 或引用 SKILL.md"
echo "  - Claude Code:   项目自带 CLAUDE.md，自动识别"
echo "  - OpenCode:      项目自带 OPENCODE.md，自动识别"
echo "  - Codex CLI:     项目自带 AGENTS.md"
