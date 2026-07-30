"""知识图谱模块 — 跨论文关系发现与 Mermaid 可视化。

图谱节点 = 论文，边 = 关系类型（引用/共享引用/同标签/同作者/方法演变）
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── 数据模型 ───────────────────────────────────────────────────────────────────

class GraphNode:
    """图谱节点：一篇论文"""
    def __init__(self, paper_id: str, title: str, tags: list[str], year: Optional[int] = None):
        self.id = paper_id
        self.title = title
        self.tags = tags
        self.year = year

    def __repr__(self):
        return f"Node({self.id})"


class GraphEdge:
    """图谱边：两篇论文之间的关系"""
    def __init__(self, source_id: str, target_id: str, relation_type: str, label: str = ""):
        self.source_id = source_id
        self.target_id = target_id
        self.relation_type = relation_type  # cites, shares_ref, same_tag, same_author, method_evolves
        self.label = label

    def __repr__(self):
        return f"Edge({self.source_id} --[{self.relation_type}]--> {self.target_id})"


class KnowledgeGraph:
    """论文知识图谱"""

    def __init__(self):
        self.nodes: dict[str, GraphNode] = {}  # paper_id → node
        self.edges: list[GraphEdge] = []

    def add_paper(self, paper_id: str, title: str, tags: list[str], year: Optional[int] = None):
        """添加或更新一个论文节点。"""
        if paper_id in self.nodes:
            self.nodes[paper_id].tags = list(set(self.nodes[paper_id].tags + tags))
            if year:
                self.nodes[paper_id].year = year
        else:
            self.nodes[paper_id] = GraphNode(paper_id, title, tags, year)

    def add_edge(self, source_id: str, target_id: str, relation_type: str, label: str = ""):
        """添加一条边（自动去重）。"""
        key = (source_id, target_id, relation_type)
        if any(
            e.source_id == source_id and e.target_id == target_id and e.relation_type == relation_type
            for e in self.edges
        ):
            return
        self.edges.append(GraphEdge(source_id, target_id, relation_type, label))

    def __repr__(self):
        return f"KnowledgeGraph({len(self.nodes)} nodes, {len(self.edges)} edges)"

    def stats(self) -> dict:
        """统计信息"""
        types = {}
        for e in self.edges:
            types[e.relation_type] = types.get(e.relation_type, 0) + 1
        return {
            "total_papers": len(self.nodes),
            "total_edges": len(self.edges),
            "edge_types": types,
        }


# ── 图谱构建器 ─────────────────────────────────────────────────────────────────


def build_graph(kb_path: str | Path = "knowledge_base/") -> KnowledgeGraph:
    """从知识库目录扫描所有论文笔记，构建知识图谱。

    Args:
        kb_path: 知识库根目录

    Returns:
        构建好的 KnowledgeGraph
    """
    kb_path = Path(kb_path)
    papers_dir = kb_path / "papers"
    graph = KnowledgeGraph()

    if not papers_dir.exists():
        return graph

    # Step 1: 扫描所有论文，提取元数据
    papers_meta: list[dict] = []
    for note_file in sorted(papers_dir.glob("*.md")):
        meta = _extract_frontmatter(note_file)
        if meta and meta.get("title"):
            paper_id = note_file.stem
            graph.add_paper(
                paper_id=paper_id,
                title=meta["title"],
                tags=meta.get("tags", []),
                year=meta.get("year"),
            )
            papers_meta.append({
                "id": paper_id,
                "title": meta["title"],
                "tags": meta.get("tags", []),
                "authors": meta.get("authors", ""),
                "year": meta.get("year"),
                "arxiv_id": meta.get("arxiv_id"),
                "content": note_file.read_text(encoding="utf-8"),
            })

    # Step 2: 发现关系
    _find_tag_relations(graph, papers_meta)
    _find_author_relations(graph, papers_meta)
    _find_citation_relations(graph, papers_meta)
    _find_method_evolution(graph, papers_meta)
    _find_shared_concepts(graph, papers_meta)

    return graph


def _extract_frontmatter(file_path: Path) -> dict:
    """从 Markdown 文件的 YAML frontmatter 提取元数据。"""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return {}

    if not content.startswith("---"):
        return {}

    # 找到 frontmatter 结束位置
    end = content.find("---", 3)
    if end == -1:
        return {}

    fm_text = content[3:end].strip()
    meta = {}

    # 简单的 YAML 解析（只处理我们需要的字段）
    for line in fm_text.split("\n"):
        line = line.strip()
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if key == "tags":
                # [tag1, tag2] 格式
                value = value.strip("[]")
                meta[key] = [t.strip().strip("'\"") for t in value.split(",") if t.strip()]
            elif key == "year":
                try:
                    meta[key] = int(value)
                except ValueError:
                    meta[key] = None
            else:
                meta[key] = value

    return meta


# ── 关系发现 ───────────────────────────────────────────────────────────────────


def _find_tag_relations(graph: KnowledgeGraph, papers: list[dict]):
    """同标签的论文之间添加边。"""
    # 按标签分组
    tag_to_papers: dict[str, list[str]] = {}
    for p in papers:
        for tag in p["tags"]:
            tag_to_papers.setdefault(tag, []).append(p["id"])

    for tag, paper_ids in tag_to_papers.items():
        if len(paper_ids) >= 2:
            for i in range(len(paper_ids)):
                for j in range(i + 1, len(paper_ids)):
                    graph.add_edge(paper_ids[i], paper_ids[j], "same_tag", tag)
                    graph.add_edge(paper_ids[j], paper_ids[i], "same_tag", tag)


def _find_author_relations(graph: KnowledgeGraph, papers: list[dict]):
    """同作者的论文之间添加边。"""
    author_to_papers: dict[str, list[str]] = {}
    for p in papers:
        authors = p.get("authors", "")
        if not authors:
            continue
        for author in authors.split(","):
            author = author.strip()
            if len(author) > 2:  # 跳过空字符
                author_to_papers.setdefault(author, []).append(p["id"])

    for author, paper_ids in author_to_papers.items():
        if len(paper_ids) >= 2:
            for i in range(len(paper_ids)):
                for j in range(i + 1, len(paper_ids)):
                    label = f"co-author: {author}"
                    graph.add_edge(paper_ids[i], paper_ids[j], "same_author", label)
                    graph.add_edge(paper_ids[j], paper_ids[i], "same_author", label)


def _find_citation_relations(graph: KnowledgeGraph, papers: list[dict]):
    """论文之间的引用关系。"""
    # 构建 arxiv_id → paper_id 映射
    arxiv_map: dict[str, str] = {}
    for p in papers:
        aid = p.get("arxiv_id")
        if aid:
            arxiv_map[aid] = p["id"]

    # 在内容中搜索 arxiv ID 引用
    for p in papers:
        content = p.get("content", "")
        for aid, cited_id in arxiv_map.items():
            if aid == p.get("arxiv_id"):
                continue
            # 搜索 arxiv:XXXX.XXXXX 或 arxiv.org/abs/XXXX.XXXXX
            if f"arxiv:{aid}" in content or f"arxiv.org/abs/{aid}" in content:
                graph.add_edge(p["id"], cited_id, "cites", f"cites {aid}")


def _find_method_evolution(graph: KnowledgeGraph, papers: list[dict]):
    """检测方法演变关系（B 基于 A 的方法发展而来）。"""
    evolution_markers = [
        "extend", "extension of", "build upon", "based on",
        "inspired by", "follow", "following", "improve upon",
        "generalize", "variant of", "successor to",
    ]

    # 对每对论文检查方法演变
    for i, p1 in enumerate(papers):
        content1_lower = (p1.get("content", "") + " " + p1["title"]).lower()
        for j, p2 in enumerate(papers):
            if i == j:
                continue
            # 检查 p1 是否提到 p2 的标题
            title2_lower = p2["title"].lower()
            # 只检测第一个有意义词（避免全文匹配）
            first_words = " ".join(title2_lower.split()[:4])
            if len(first_words) < 10:
                continue

            if first_words in content1_lower:
                # 检查上下文是否有演变标记
                idx = content1_lower.find(first_words)
                context = content1_lower[max(0, idx-100):idx+len(first_words)+100]
                if any(marker in context for marker in evolution_markers):
                    graph.add_edge(p1["id"], p2["id"], "method_evolves", "builds upon")


def _find_shared_concepts(graph: KnowledgeGraph, papers: list[dict]):
    """检测共享关键词/概念的论文。"""
    # 对每对论文，计算共享的关键概念
    for i in range(len(papers)):
        words1 = set(_extract_key_concepts(papers[i]["title"]))
        for j in range(i + 1, len(papers)):
            words2 = set(_extract_key_concepts(papers[j]["title"]))
            shared = words1 & words2
            # 至少 2 个共享概念（不包括 common words）
            significant = [w for w in shared if len(w) > 3 and w not in _COMMON_WORDS]
            if len(significant) >= 2:
                label = f"shared: {', '.join(sorted(significant)[:3])}"
                graph.add_edge(papers[i]["id"], papers[j]["id"], "shared_concept", label)
                graph.add_edge(papers[j]["id"], papers[i]["id"], "shared_concept", label)


_COMMON_WORDS = {
    "this", "that", "with", "from", "have", "been", "were", "they",
    "their", "which", "based", "using", "method", "approach", "model",
    "network", "learning", "paper", "novel", "improved", "efficient",
    "large", "small", "deep", "neural", "data", "training",
}


def _extract_key_concepts(title: str) -> list[str]:
    """从标题中提取关键概念词。"""
    # 简单分词
    words = re.findall(r"[a-zA-Z]+", title.lower())
    # 过滤太短的
    return [w for w in words if len(w) > 3]


# ── Mermaid 图表生成 ───────────────────────────────────────────────────────────


def to_mermaid(graph: KnowledgeGraph, relation_filter: Optional[list[str]] = None) -> str:
    """将知识图谱导出为 Mermaid 图表。

    Args:
        graph: 知识图谱
        relation_filter: 只包含指定关系类型，None 表示全部

    Returns:
        Mermaid 语法的图表字符串，可直接嵌入 Markdown
    """
    lines = ["```mermaid", "graph TD"]

    edges = graph.edges
    if relation_filter:
        edges = [e for e in edges if e.relation_type in relation_filter]

    # 关系类型 → 线型
    edge_styles = {
        "cites": "==>",
        "same_tag": "---",
        "same_author": "-..->",
        "method_evolves": "==>",
        "shared_concept": "-.->",
    }

    # 关系类型 → 颜色（Mermaid style）
    link_styles = {
        "cites": "stroke:#4a9eff,stroke-width:2px",
        "same_tag": "stroke:#888,stroke-dasharray: 5 5",
        "same_author": "stroke:#ff6b6b,stroke-dasharray: 3 3",
        "method_evolves": "stroke:#51cf66,stroke-width:2px",
        "shared_concept": "stroke:#f08d49,stroke-dasharray: 5 5",
    }

    seen_edges = set()
    for edge in edges:
        edge_key = (edge.source_id, edge.target_id, edge.relation_type)
        if edge_key in seen_edges:
            continue
        seen_edges.add(edge_key)

        style = edge_styles.get(edge.relation_type, "---")
        source = _safe_id(edge.source_id)
        target = _safe_id(edge.target_id)
        label = edge.label if edge.label else edge.relation_type
        label = _safe_label(label)
        lines.append(f"    {source}[{_short_label(edge.source_id, graph)}] {style}|{label}| {target}[{_short_label(edge.target_id, graph)}]")

    # 添加样式定义
    lines.append("")
    for rel_type, style in link_styles.items():
        lines.append(f"    linkStyle default {style}")
    lines.append("```")

    return "\n".join(lines)


def to_mermaid_stats(graph: KnowledgeGraph) -> str:
    """生成图谱统计的 Mermaid 饼图。"""
    stats = graph.stats()
    lines = ["```mermaid", "pie title 知识图谱关系分布"]
    for rel_type, count in stats["edge_types"].items():
        rel_labels = {
            "same_tag": "同标签",
            "same_author": "同作者",
            "cites": "引用关系",
            "method_evolves": "方法演化",
            "shared_concept": "共享概念",
        }
        label = rel_labels.get(rel_type, rel_type)
        lines.append(f'    "{label}" : {count}')
    lines.append("```")
    return "\n".join(lines)


def _safe_id(paper_id: str) -> str:
    """转换为 Mermaid 安全 ID。"""
    # 去除特殊字符
    return re.sub(r"[^a-zA-Z0-9]", "_", paper_id)


def _safe_label(label: str) -> str:
    """清理边标签。"""
    return label.replace('"', "'").replace("|", "/")[:50]


def _short_label(paper_id: str, graph: KnowledgeGraph) -> str:
    """获取节点简短标签。"""
    node = graph.nodes.get(paper_id)
    if node:
        title = node.title[:40]
        if node.year:
            title += f" ({node.year})"
        return title.replace('"', "'")
    return paper_id


# ── 增量更新 ───────────────────────────────────────────────────────────────────


def update_graph(kb_path: str | Path = "knowledge_base/") -> KnowledgeGraph:
    """增量更新知识图谱（处理新增和修改的论文）。

    与 build_graph() 的区别：增量模式只更新变更的论文节点和边，
    但为简单起见，当前实现为全量重建（论文量不大时效率足够）。

    Args:
        kb_path: 知识库根目录

    Returns:
        更新后的知识图谱
    """
    return build_graph(kb_path)


def export_graph_markdown(
    kb_path: str | Path = "knowledge_base/",
    output_path: Optional[str | Path] = None,
) -> str:
    """导出知识图谱为 Markdown 文件（包含统计 + Mermaid 图）。

    Args:
        kb_path: 知识库根目录
        output_path: 输出路径，None 则保存到 knowledge_base/graph.md

    Returns:
        生成的 Markdown 文本
    """
    graph = build_graph(kb_path)
    stats = graph.stats()

    lines = [
        "# 📊 论文知识图谱",
        "",
        f"*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        "",
        f"## 统计",
        f"- 📄 **论文总数**: {stats['total_papers']}",
        f"- 🔗 **关系总数**: {stats['total_edges']}",
        "",
    ]

    # 关系类型分布
    if stats["edge_types"]:
        lines.append("### 关系分布\n")
        rel_labels = {
            "same_tag": "🏷️ 同标签",
            "same_author": "👤 同作者",
            "cites": "📎 引用关系",
            "method_evolves": "🌱 方法演化",
            "shared_concept": "💡 共享概念",
        }
        lines.append("| 关系类型 | 数量 |")
        lines.append("|---------|------|")
        for rel_type, count in sorted(stats["edge_types"].items(), key=lambda x: -x[1]):
            label = rel_labels.get(rel_type, rel_type)
            lines.append(f"| {label} | {count} |")
        lines.append("")

    # Mermaid 图
    lines.append("## 图谱可视化\n")
    lines.append(to_mermaid(graph))
    lines.append("")

    lines.append("## 关系分布图\n")
    lines.append(to_mermaid_stats(graph))
    lines.append("")

    # 论文列表
    lines.append("## 论文节点\n")
    lines.append("| ID | 标题 | 年份 | 标签 |")
    lines.append("|---|------|------|------|")
    for node in sorted(graph.nodes.values(), key=lambda n: n.year or 0, reverse=True):
        tags = ", ".join(node.tags[:4])
        lines.append(f"| {node.id} | {node.title[:50]} | {node.year or '?'} | {tags} |")

    text = "\n".join(lines)

    # 保存文件
    if output_path is None:
        output_path = Path(kb_path) / "graph.md"
    Path(output_path).write_text(text, encoding="utf-8")

    return text
