"""交互问答：基于已解析的论文上下文做对话。

Agent 加载此模块后，用户可以针对论文内容提问，
Q&A 引擎基于论文全文和已有分析结果进行回答。
"""

from __future__ import annotations

from typing import Optional

from .paper import ParsedPaper


def ask_about_paper(
    question: str,
    paper: ParsedPaper,
    context: Optional[dict] = None,
) -> str:
    """基于论文上下文回答用户问题。

    构建包含论文摘要、章节结构和用户问题的 prompt，
    供 Agent 调用 LLM 生成回答。

    Args:
        question: 用户的自然语言问题
        paper: 解析后的结构化论文
        context: 可选的分析结果上下文（如费曼拆解、创新分析等）

    Returns:
        回答 prompt（Agent 用此调用 LLM 获取回答）
    """
    parts = []

    # 论文基本信息
    parts.append(f"# 论文: {paper.title}")
    if paper.authors:
        authors = ", ".join(a.name for a in paper.authors[:5])
        parts.append(f"作者: {authors}")
    if paper.year:
        parts.append(f"年份: {paper.year}")
    parts.append("")

    # 摘要
    if paper.abstract:
        parts.append(f"## 摘要\n{paper.abstract}\n")

    # 章节结构概览
    if paper.sections:
        parts.append("## 章节结构\n")
        for sec in paper.sections:
            indent = "  " * (sec.level - 1)
            preview = sec.content[:80].replace("\n", " ")
            parts.append(f"{indent}- {sec.heading}: {preview}...")
        parts.append("")

    # 已有分析上下文（如果有）
    if context:
        parts.append("## 已有分析\n")
        for key, value in context.items():
            if value:
                summary = value[:300].replace("\n", " ")
                parts.append(f"- **{key}**: {summary}...")
        parts.append("")

    # 用户问题
    parts.append("---")
    parts.append(f"## ❓ 用户问题\n{question}\n")
    parts.append("请基于以上论文内容回答用户问题。")
    parts.append("- 如果问题答案在论文中有明确说明，请标注出处（章节/段落）")
    parts.append("- 如果论文中没有明确说明，给出基于上下文的合理推断并标注'推测'")
    parts.append("- 不要编造论文没有的信息")

    return "\n".join(parts)


def search_paper(
    query: str,
    paper: ParsedPaper,
    max_results: int = 5,
) -> list[dict]:
    """在论文中搜索关键词，返回匹配的段落。

    Args:
        query: 搜索关键词
        paper: 解析后的论文
        max_results: 最多返回结果数

    Returns:
        [{section, content_snippet, match_excerpt}, ...]
    """
    results = []
    query_lower = query.lower()

    # 搜标题
    if query_lower in paper.title.lower():
        results.append({
            "section": "标题",
            "content_snippet": paper.title,
            "match_excerpt": paper.title,
        })

    # 搜摘要
    if query_lower in paper.abstract.lower():
        idx = paper.abstract.lower().find(query_lower)
        start = max(0, idx - 40)
        end = min(len(paper.abstract), idx + len(query) + 40)
        results.append({
            "section": "摘要",
            "content_snippet": paper.abstract[start:end],
            "match_excerpt": f"…{paper.abstract[start:end]}…",
        })

    # 搜各章节
    for sec in paper.sections:
        if query_lower in sec.content.lower():
            idx = sec.content.lower().find(query_lower)
            start = max(0, idx - 40)
            end = min(len(sec.content), idx + len(query) + 40)
            results.append({
                "section": sec.heading,
                "content_snippet": sec.content[start:end],
                "match_excerpt": f"…{sec.content[start:end]}…",
            })
            if len(results) >= max_results:
                break

    return results


def summarize_section(paper: ParsedPaper, section_name: str) -> str:
    """获取指定章节的总结。

    Args:
        paper: 解析后的论文
        section_name: 章节名称（模糊匹配）

    Returns:
        该章节的内容（供 Agent 进一步总结）
    """
    section_name_lower = section_name.lower()

    # 查找匹配的章节
    for sec in paper.sections:
        if section_name_lower in sec.heading.lower():
            return f"## {sec.heading}\n\n{sec.content}"

    # 找不到精确匹配，列出所有章节
    available = "\n".join(f"- {s.heading}" for s in paper.sections)
    return (
        f"未找到章节 '{section_name}'。论文有以下章节：\n\n{available}"
    )
