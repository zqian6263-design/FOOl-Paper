"""论文自动分类与知识库管理。

- classify_and_store(): 自动标签 + 生成 Markdown 笔记 + 入库
- 更新 knowledge_base/index.md 全局索引
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from .paper import ParsedPaper
from .reporter import generate_report


# ── 已知标签体系 ───────────────────────────────────────────────────────────────

# 学科领域标签
_DOMAIN_TAGS = {
    # 计算机科学
    "deep learning": "深度学习",
    "machine learning": "机器学习",
    "neural network": "神经网络",
    "reinforcement learning": "强化学习",
    "generative adversarial": "GAN",
    "diffusion model": "扩散模型",
    "transformer": "Transformer",
    "attention": "Attention",
    "large language model": "大语言模型",
    "language model": "语言模型",
    "computer vision": "计算机视觉",
    "image": "图像处理",
    "object detection": "目标检测",
    "segmentation": "图像分割",
    "nlp": "自然语言处理",
    "natural language": "自然语言处理",
    "speech": "语音处理",
    "audio": "音频处理",
    "graph": "图神经网络",
    "knowledge graph": "知识图谱",
    "recommendation": "推荐系统",
    # 数学/理论
    "optimization": "优化理论",
    "probability": "概率论",
    "statistics": "统计学习",
    "information theory": "信息论",
    "game theory": "博弈论",
    # 交叉学科
    "bioinformatics": "生物信息学",
    "computational biology": "计算生物学",
    "robotics": "机器人",
    "autonomous": "自动驾驶",
    "healthcare": "医疗AI",
    "finance": "金融科技",
}


def _auto_tag(paper: ParsedPaper) -> list[str]:
    """基于标题 + 摘要 + 关键词自动分配标签。

    Args:
        paper: 解析后的论文

    Returns:
        标签列表
    """
    text = (paper.title + " " + paper.abstract).lower()
    tags: set[str] = set()

    for keyword, tag in _DOMAIN_TAGS.items():
        if keyword in text:
            tags.add(tag)

    # 从 arxiv 分类推断
    for kw in paper.keywords:
        if "cs.CL" in kw or "cs.LG" in kw:
            tags.add("机器学习")

    # 至少有一个标签
    if not tags:
        tags.add("未分类")

    return sorted(tags)


def _generate_paper_id(paper: ParsedPaper) -> str:
    """为论文生成唯一的文件 ID。

    优先使用 arxiv_id，否则用标题 → 下划线命名。
    """
    if paper.arxiv_id:
        return paper.arxiv_id

    # 标题 → slug
    title = paper.title.lower()
    # 只保留字母数字
    title = re.sub(r"[^a-z0-9]", "-", title)
    # 压缩多个连字符
    title = re.sub(r"-+", "-", title)
    # 截断
    if len(title) > 60:
        title = title[:60].rstrip("-")
    return title.strip("-") or "unnamed"


# ── 主流入口 ───────────────────────────────────────────────────────────────────


def classify_and_store(
    paper: ParsedPaper,
    analysis_result: Optional[dict] = None,
    kb_path: str | Path = "knowledge_base/",
) -> str:
    """自动归类论文并存入知识库。

    Args:
        paper: 解析后的论文
        analysis_result: 可选的分析结果（用于填充笔记内容）
        kb_path: 知识库根目录

    Returns:
        生成的笔记文件绝对路径
    """
    kb_path = Path(kb_path).resolve()
    papers_dir = kb_path / "papers"
    papers_dir.mkdir(parents=True, exist_ok=True)

    # 生成标签
    tags = _auto_tag(paper)

    # 生成文件名
    paper_id = _generate_paper_id(paper)
    note_path = papers_dir / f"{paper_id}.md"

    # 生成笔记内容
    note = _build_note(paper, tags, analysis_result)

    # 写入
    note_path.write_text(note, encoding="utf-8")

    # 更新索引
    _update_index(kb_path, paper, tags, note_path)

    return str(note_path)


def _build_note(
    paper: ParsedPaper,
    tags: list[str],
    analysis_result: Optional[dict] = None,
) -> str:
    """构建论文笔记的 Markdown 文件。"""
    lines = [
        "---",
        f"title: \"{paper.title}\"",
    ]

    if paper.authors:
        authors_yaml = ", ".join(a.name for a in paper.authors)
        lines.append(f"authors: \"{authors_yaml}\"")

    if paper.year:
        lines.append(f"year: {paper.year}")

    if paper.arxiv_id:
        lines.append(f"arxiv_id: \"{paper.arxiv_id}\"")

    if paper.doi:
        lines.append(f"doi: \"{paper.doi}\"")

    tags_yaml = ", ".join(tags)
    lines.append(f"tags: [{tags_yaml}]")
    lines.append(f"date_read: \"{datetime.now().strftime('%Y-%m-%d')}\"")
    lines.append("---\n")

    lines.append(f"# {paper.title}\n")

    if paper.authors:
        authors_str = ", ".join(a.name for a in paper.authors[:5])
        if len(paper.authors) > 5:
            authors_str += f" 等 ({len(paper.authors)} 人)"
        lines.append(f"**作者**: {authors_str}\n")

    if paper.year:
        lines.append(f"**年份**: {paper.year}\n")

    if paper.arxiv_id:
        lines.append(f"**arxiv**: [{paper.arxiv_id}](https://arxiv.org/abs/{paper.arxiv_id})\n")

    if tags:
        tags_str = " ".join(f"`{t}`" for t in tags)
        lines.append(f"\n{tags_str}\n")

    if paper.abstract:
        lines.append("## 摘要\n")
        lines.append(paper.abstract + "\n")

    # 分析结果（如果有）
    if analysis_result:
        for key in ["feynman", "first_principles", "innovation", "replication"]:
            if key in analysis_result and analysis_result[key]:
                lines.append(f"## {_task_heading(key)}\n")
                lines.append(analysis_result[key] + "\n")

    lines.append("## 我的思考\n")
    lines.append("> *阅读后的个人笔记和想法…*\n")

    return "\n".join(lines)


_TASK_HEADINGS = {
    "feynman": "费曼拆解",
    "first_principles": "第一性原理分析",
    "innovation": "创新与不足",
    "replication": "复现分析",
    "translation": "翻译",
}


def _task_heading(key: str) -> str:
    return _TASK_HEADINGS.get(key, key)


# ── 索引管理 ───────────────────────────────────────────────────────────────────


def _update_index(
    kb_path: Path,
    paper: ParsedPaper,
    tags: list[str],
    note_path: Path,
) -> None:
    """更新知识库全局索引。"""
    index_path = kb_path / "index.md"

    # 如果索引文件不存在，创建一个
    if not index_path.exists():
        index_path.write_text(
            "# FOOL-paper 知识库\n\n"
            "> 自动生成的全局索引。\n\n"
            f"*最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n",
            encoding="utf-8",
        )

    content = index_path.read_text(encoding="utf-8")

    # 找到 "## 论文列表" 部分或追加
    entry_line = (
        f"- [{paper.title}](papers/{note_path.name}) "
        f"| {paper.year or '?'} "
        f"| {' `'.join(tags)}"
    )

    if "## 论文列表" in content:
        # 在列表末尾追加
        content = content.rstrip() + f"\n{entry_line}\n"
    else:
        content += f"\n## 论文列表\n\n{entry_line}\n"

    # 更新最后修改时间
    content = re.sub(
        r"\*最后更新:.*\*",
        f"*最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        content,
    )

    index_path.write_text(content, encoding="utf-8")


def get_kb_stats(kb_path: str | Path = "knowledge_base/") -> dict:
    """获取知识库统计信息。

    Returns:
        {total_papers, tags: {tag: count}, last_updated}
    """
    kb_path = Path(kb_path)
    papers_dir = kb_path / "papers"

    if not papers_dir.exists():
        return {"total_papers": 0, "tags": {}, "last_updated": None}

    papers = list(papers_dir.glob("*.md"))
    tag_counts: dict[str, int] = {}

    for paper_file in papers:
        content = paper_file.read_text(encoding="utf-8")
        # 从 YAML frontmatter 中提取 tags
        tag_match = re.search(r"tags:\s*\[(.*?)\]", content)
        if tag_match:
            for tag in tag_match.group(1).split(","):
                tag = tag.strip()
                if tag:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # 最近修改时间
    last_updated = None
    if papers:
        latest = max(p.stat().st_mtime for p in papers)
        last_updated = datetime.fromtimestamp(latest).strftime('%Y-%m-%d %H:%M')

    return {
        "total_papers": len(papers),
        "tags": tag_counts,
        "last_updated": last_updated,
    }
