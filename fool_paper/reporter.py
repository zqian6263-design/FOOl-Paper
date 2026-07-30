"""阅读报告生成器：将分析结果组装为结构化 Markdown 笔记。"""

from __future__ import annotations

from datetime import datetime

from .paper import AnalysisResult, ComplexityLevel, ParsedPaper


def generate_report(result: AnalysisResult, format: str = "markdown") -> str:
    """生成结构化阅读报告。

    Args:
        result: 分析结果（包含 paper 和各分析任务的输出）
        format: 输出格式，目前仅支持 "markdown"

    Returns:
        格式化的 Markdown 报告文本
    """
    if format != "markdown":
        raise ValueError(f"不支持的输出格式: {format!r}。仅支持 'markdown'。")

    paper = result.paper
    lines: list[str] = []

    # ── 标题与元数据 ──────────────────────────────────────────────────
    lines.append(_build_header(paper, result))

    # ── 摘要 ──────────────────────────────────────────────────────────
    lines.append(_build_abstract(paper))

    # ── 翻译 ──────────────────────────────────────────────────────────
    if result.translation:
        lines.append(result.translation)
        lines.append("")

    # ── 费曼拆解 ──────────────────────────────────────────────────────────
    if result.feynman:
        lines.append(result.feynman)
        lines.append("")

    # ── 第一性原理 ──────────────────────────────────────────────────────────
    if result.first_principles:
        lines.append(result.first_principles)
        lines.append("")

    # ── 创新与不足 ──────────────────────────────────────────────────────────
    if result.innovation:
        lines.append(result.innovation)
        lines.append("")

    # ── 复现分析 ──────────────────────────────────────────────────────────
    if result.replication:
        lines.append(result.replication)
        lines.append("")

    # ── 公式理解 ──────────────────────────────────────────────────────────
    if result.formula_explanations:
        lines.append("## 📐 公式理解\n")
        lines.append(result.formula_explanations)
        lines.append("")

    # ── 分类信息 ──────────────────────────────────────────────────────────
    if result.tags or result.category:
        lines.append(_build_classification(result))
        lines.append("")

    # ── 我的思考（空白模板） ────────────────────────────────────────────
    lines.append(_build_thoughts())

    # ── 引用 ──────────────────────────────────────────────────────────
    if paper.references:
        lines.append(_build_references(paper))

    # ── 页脚 ──────────────────────────────────────────────────────────
    lines.append(_build_footer(result))

    report = "\n\n".join(lines)
    return report


def _build_header(paper: ParsedPaper, result: AnalysisResult) -> str:
    """构建报告头部。"""
    parts = [f"# {paper.title}\n"]

    # 元数据标签
    meta_items = []
    if paper.authors:
        authors = ", ".join(a.name for a in paper.authors[:5])
        if len(paper.authors) > 5:
            authors += f" 等 ({len(paper.authors)} 人)"
        meta_items.append(authors)
    if paper.year:
        meta_items.append(str(paper.year))
    if paper.venue:
        meta_items.append(paper.venue)
    if paper.arxiv_id:
        meta_items.append(f"[arxiv:{paper.arxiv_id}](https://arxiv.org/abs/{paper.arxiv_id})")

    if meta_items:
        parts.append(f"> {' | '.join(meta_items)}\n")

    # 标签
    if result.tags:
        tags_str = " ".join(f"`{t}`" for t in result.tags)
        parts.append(f"**标签**: {tags_str}\n")

    return "\n".join(parts)


def _build_abstract(paper: ParsedPaper) -> str:
    """构建摘要部分。"""
    lines = ["## 📝 摘要\n"]
    if paper.abstract:
        lines.append(paper.abstract)
    else:
        lines.append("*(未提取到摘要)*")
    return "\n".join(lines)


def _build_classification(result: AnalysisResult) -> str:
    """构建分类信息。"""
    lines = ["## 📁 分类信息\n"]
    if result.category:
        lines.append(f"- **主分类**: {result.category}")
    if result.tags:
        tags = ", ".join(result.tags)
        lines.append(f"- **标签**: {tags}")
    return "\n".join(lines)


def _build_thoughts() -> str:
    """构建个人思考模板（占位，Agent 必须填充实内容）。"""
    return """## 我的思考

> ⚠️ Agent 必须填充至少 3-5 句实际内容，禁止保留此占位符。"""


def _build_references(paper: ParsedPaper, limit: int = 10) -> str:
    """构建参考文献列表。"""
    lines = ["## 📎 参考文献\n"]
    for i, ref in enumerate(paper.references[:limit]):
        year_str = f" ({ref.year})" if ref.year else ""
        lines.append(f"{i + 1}. {ref.title}{year_str}")
    if len(paper.references) > limit:
        lines.append(f"\n*...（共 {len(paper.references)} 篇参考文献，此处仅列出前 {limit} 篇）*")
    return "\n".join(lines)


def _build_footer(result: AnalysisResult) -> str:
    """构建报告页脚。"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    footer_parts = [
        "---",
        f"*由 [FOOL-paper](https://github.com/zqian6263-design/FOOl-Paper) 生成*",
    ]
    if result.model_used:
        footer_parts.append(f"*模型: {result.model_used}*")
    if result.effort_used:
        footer_parts.append(f"*复杂度: {result.effort_used}*")
    if result.analysis_time_seconds:
        footer_parts.append(f"*耗时: {result.analysis_time_seconds:.0f}s*")
    footer_parts.append(f"*生成时间: {now}*")
    return "\n".join(footer_parts)
