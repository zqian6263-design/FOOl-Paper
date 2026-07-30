#!/usr/bin/env bash
# FoolPaper — 一键安装脚本
# 用法: bash install.sh [target-dir]
# 默认部署到 Hermes Agent 技能目录

set -euo pipefail

SKILL_DIR="${1:-$HOME/AppData/Local/hermes/skills/research/fool-paper}"

echo "📦 部署 FoolPaper 到: $SKILL_DIR"

# 创建技能目录
mkdir -p "$SKILL_DIR/paper_pal"
mkdir -p "$SKILL_DIR/prompts"
mkdir -p "$SKILL_DIR/tests/fixtures"

# 部署核心文件
install -m 644 SKILL.md "$SKILL_DIR/SKILL.md"
install -m 644 AGENTS.md "$SKILL_DIR/AGENTS.md" 2>/dev/null || true
install -m 644 pyproject.toml "$SKILL_DIR/pyproject.toml" 2>/dev/null || true

# 部署 prompt 模板
for f in prompts/*.md; do
    install -m 644 "$f" "$SKILL_DIR/prompts/"
done

# 部署 Python 包
if [ -f paper_pal/__init__.py ]; then
    install -m 644 paper_pal/__init__.py "$SKILL_DIR/paper_pal/"
fi

echo "✅ 部署完成"
echo ""
echo "下一步："
echo "  1. 确保 Hermes Agent 已重启"
echo "  2. 说: \"帮我读这篇论文 arxiv:2106.09685\""
echo ""
echo "或者手动加载 SKILL.md:"
echo "  Hermes: SKILL.md 会自动加载"
echo "  Claude Code: 将 SKILL.md 放入项目根目录"
echo "  OpenCode: 引用 SKILL.md 中的能力定义"
