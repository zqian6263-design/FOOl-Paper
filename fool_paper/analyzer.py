"""LLM 分析引擎：翻译、费曼拆解、创新分析、复现分析。

将 LLM 调用集中于此模块，方便缓存和模型路由。
每个函数接收 ParsedPaper，load prompts/ 模板，构建完整 prompt。
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from .paper import ComplexityLevel, ParsedPaper

# ── Prompt 模板加载 ────────────────────────────────────────────────────────────

# prompts 目录路径（相对于 fool_paper 包）
_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def _load_prompt(name: str) -> str:
    """加载一个 prompt 模板文件。

    Args:
        name: prompt 文件名（不含 .md），如 "feynman-deconstruction"

    Returns:
        prompt 模板全文
    """
    path = _PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        # 回退：按名称查找
        for candidate in _PROMPTS_DIR.glob("*.md"):
            if candidate.stem == name or name in candidate.stem:
                path = candidate
                break

    if not path.exists():
        raise FileNotFoundError(
            f"找不到 prompt 模板: {name}.md。"
            f"搜索路径: {_PROMPTS_DIR}"
        )

    return path.read_text(encoding="utf-8")


# ── 文本截断工具 ─────────────────────────────────────────────────────────────────

def _truncate_text(text: str, max_chars: int = 8000) -> str:
    """截断文本到指定长度，保留完整的段落。"""
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    # 在最后一个完整段落处截断
    last_newline = truncated.rfind("\n\n")
    if last_newline > max_chars // 2:
        return truncated[:last_newline] + "\n\n[... 后续内容已截断 ...]"
    return truncated + "\n\n[... 后续内容已截断 ...]"


def _paper_context(paper: ParsedPaper) -> str:
    """生成论文的上下文摘要文本，用于注入 prompt。"""
    parts = []

    parts.append(f"# 论文信息")
    parts.append(f"标题: {paper.title}")

    if paper.authors:
        authors_str = ", ".join(a.name for a in paper.authors[:10])
        parts.append(f"作者: {authors_str}")

    if paper.year:
        parts.append(f"年份: {paper.year}")

    parts.append("")

    if paper.abstract:
        parts.append(f"## 摘要\n{paper.abstract}\n")

    # 正文（截断）
    text_parts = []
    for sec in paper.sections[:10]:  # 最多前 10 节
        text_parts.append(f"{'#' * sec.level} {sec.heading}\n{sec.content}")
    full_text = "\n\n".join(text_parts)

    parts.append(f"## 正文\n{_truncate_text(full_text, max_chars=6000)}")

    return "\n\n".join(parts)


# ── Prompt 构建函数 ─────────────────────────────────────────────────────────────


def build_translate_prompt(paper: ParsedPaper) -> str:
    """构建翻译 + 术语解释的完整 prompt。

    Args:
        paper: 解析后的论文

    Returns:
        完整的 LLM prompt
    """
    template = _load_prompt("translation")
    ctx = _paper_context(paper)

    prompt = (
        f"{template}\n\n"
        f"--- 论文内容 ---\n\n"
        f"{ctx}"
    )
    return prompt


def build_feynman_prompt(paper: ParsedPaper) -> str:
    """构建费曼拆解的完整 prompt。"""
    template = _load_prompt("feynman-deconstruction")
    ctx = _paper_context(paper)

    prompt = (
        f"{template}\n\n"
        f"--- 论文内容 ---\n\n"
        f"{ctx}"
    )
    return prompt


def build_first_principles_prompt(paper: ParsedPaper) -> str:
    """构建第一性原理分析的完整 prompt。"""
    template = _load_prompt("first-principles")
    ctx = _paper_context(paper)

    prompt = (
        f"{template}\n\n"
        f"--- 论文内容 ---\n\n"
        f"{ctx}"
    )
    return prompt


def build_innovation_prompt(paper: ParsedPaper) -> str:
    """构建创新点分析的完整 prompt。"""
    template = _load_prompt("innovation-analysis")
    ctx = _paper_context(paper)

    prompt = (
        f"{template}\n\n"
        f"--- 论文内容 ---\n\n"
        f"{ctx}"
    )
    return prompt


def build_replication_prompt(paper: ParsedPaper) -> str:
    """构建复现分析的完整 prompt。"""
    template = _load_prompt("replication-guide")
    ctx = _paper_context(paper)

    prompt = (
        f"{template}\n\n"
        f"--- 论文内容 ---\n\n"
        f"{ctx}"
    )
    return prompt


# ── Prompt 构建映射表 ──────────────────────────────────────────────────────────

# 任务名 → (build 函数, task key)
_TASK_BUILDERS: dict[str, str] = {
    "translate": "translate",
    "feynman": "feynman",
    "first_principles": "first_principles",
    "innovation": "innovation",
    "replication": "replication",
}

_BUILD_FUNCTIONS = {
    "translate": build_translate_prompt,
    "feynman": build_feynman_prompt,
    "first_principles": build_first_principles_prompt,
    "innovation": build_innovation_prompt,
    "replication": build_replication_prompt,
}


# ── 主入口 ──────────────────────────────────────────────────────────────────────


def build_prompts(
    paper: ParsedPaper,
    tasks: list[str],
    effort: ComplexityLevel = ComplexityLevel.MEDIUM,
) -> dict[str, str]:
    """为指定任务列表构建 LLM prompt。

    Args:
        paper: 解析后的结构化论文
        tasks: 任务列表，可选值:
            - "translate": 翻译 + 术语解释
            - "feynman": 费曼拆解
            - "first_principles": 第一性原理分析
            - "innovation": 创新点+不足+改进方向
            - "replication": 复现分析
        effort: 复杂度等级（保留字段，未来用于 Effort 级别调整）

    Returns:
        {task_name: prompt_text} 字典

    Raises:
        ValueError: 未知的 task name
    """
    prompts = {}
    for task in tasks:
        task_lower = task.lower()
        if task_lower not in _BUILD_FUNCTIONS:
            raise ValueError(
                f"未知的分析任务: {task!r}。"
                f"可选值: {list(_BUILD_FUNCTIONS.keys())}"
            )
        prompts[task_lower] = _BUILD_FUNCTIONS[task_lower](paper)
    return prompts


def analyze(
    paper: ParsedPaper,
    tasks: list[str],
    effort: ComplexityLevel = ComplexityLevel.MEDIUM,
    model: Optional[str] = None,
) -> dict[str, str]:
    """对论文执行指定分析任务（构建 prompt）。

    当前版本返回构建好的 prompt，由调用方（Agent）执行 LLM 调用。
    这样设计是为了让 Hermes/Claude Code/OpenCode 等 Agent 用自带的 LLM
    能力执行分析，而不是要求安装额外的 LLM SDK。

    Args:
        paper: 解析后的结构化论文
        tasks: 任务列表
        effort: 复杂度等级
        model: 模型名称（保留给未来版本）

    Returns:
        {task_name: prompt_for_llm} 字典
    """
    return build_prompts(paper, tasks, effort)


# ── 便捷函数（直接返回 prompt）───────────────────────────────────────────────────


def translate_section(paper: ParsedPaper) -> str:
    """翻译论文（返回构建好的 prompt）。"""
    return build_translate_prompt(paper)


def feynman_deconstruction(paper: ParsedPaper) -> str:
    """费曼拆解（返回构建好的 prompt）。"""
    return build_feynman_prompt(paper)


def first_principles_analysis(paper: ParsedPaper) -> str:
    """第一性原理分析（返回构建好的 prompt）。"""
    return build_first_principles_prompt(paper)


def innovation_analysis(paper: ParsedPaper) -> str:
    """创新点、不足、改进方向（返回构建好的 prompt）。"""
    return build_innovation_prompt(paper)


def replication_analysis(paper: ParsedPaper) -> str:
    """复现分析（返回构建好的 prompt）。"""
    return build_replication_prompt(paper)
