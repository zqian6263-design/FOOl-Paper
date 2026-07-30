"""测试 knowledge_graph.py"""

import tempfile
from pathlib import Path

from fool_paper.knowledge_graph import (
    KnowledgeGraph,
    GraphNode,
    GraphEdge,
    _extract_frontmatter,
    _extract_key_concepts,
    build_graph,
    to_mermaid,
    to_mermaid_stats,
    export_graph_markdown,
)
from fool_paper.organizer import classify_and_store
from fool_paper.paper import Author, ParsedPaper


def test_empty_graph():
    """空图谱"""
    graph = KnowledgeGraph()
    assert len(graph.nodes) == 0
    assert len(graph.edges) == 0
    assert graph.stats()["total_papers"] == 0


def test_add_node():
    """添加节点"""
    graph = KnowledgeGraph()
    graph.add_paper("1706.03762", "Transformer", ["NLP", "深度学习"], 2017)
    assert len(graph.nodes) == 1
    assert graph.nodes["1706.03762"].title == "Transformer"


def test_add_edge():
    """添加边"""
    graph = KnowledgeGraph()
    graph.add_paper("a", "Paper A", ["NLP"])
    graph.add_paper("b", "Paper B", ["NLP"])
    graph.add_edge("a", "b", "same_tag", "NLP")
    assert len(graph.edges) == 1


def test_add_edge_dedup():
    """重复边去重"""
    graph = KnowledgeGraph()
    graph.add_paper("a", "A", [])
    graph.add_paper("b", "B", [])
    graph.add_edge("a", "b", "same_tag", "NLP")
    graph.add_edge("a", "b", "same_tag", "NLP")
    assert len(graph.edges) == 1


def test_extract_frontmatter():
    """从 Markdown 提取 frontmatter"""
    content = """---
title: "Test Paper"
year: 2023
tags: [NLP, Transformer]
authors: "Smith, J."
---

# Content"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(content)
        tmp_path = f.name

    try:
        meta = _extract_frontmatter(Path(tmp_path))
        assert meta["title"] == "Test Paper"
        assert meta["year"] == 2023
        assert meta["tags"] == ["NLP", "Transformer"]
        assert meta["authors"] == "Smith, J."
    finally:
        Path(tmp_path).unlink()


def test_extract_key_concepts():
    """从标题提取关键概念"""
    concepts = _extract_key_concepts("Attention Is All You Need")
    assert "attention" in concepts


def test_build_graph_empty():
    """空知识库返回空图谱"""
    with tempfile.TemporaryDirectory() as tmpdir:
        graph = build_graph(tmpdir)
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0


def test_build_graph_with_papers():
    """包含论文的知识库构建图谱"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 添加 Transformer 论文
        paper1 = ParsedPaper(
            title="Attention Is All You Need",
            abstract="We propose the Transformer based on attention.",
            year=2017,
            arxiv_id="1706.03762",
        )
        classify_and_store(paper1, kb_path=tmpdir)

        # 添加 BERT 论文
        paper2 = ParsedPaper(
            title="BERT: Pre-training of Deep Bidirectional Transformers",
            abstract="We introduce BERT, a language model based on Transformer.",
            year=2019,
            arxiv_id="1810.04805",
        )
        classify_and_store(paper2, kb_path=tmpdir)

        # 构建图谱
        graph = build_graph(tmpdir)
        assert len(graph.nodes) >= 2
        # 应该至少有同标签边
        assert len(graph.edges) >= 1


def test_to_mermaid():
    """Mermaid 导出"""
    graph = KnowledgeGraph()
    graph.add_paper("a", "Transformer", ["NLP"], 2017)
    graph.add_paper("b", "BERT", ["NLP"], 2019)
    graph.add_edge("a", "b", "same_tag", "NLP")

    mermaid = to_mermaid(graph)
    assert "```mermaid" in mermaid
    assert "graph TD" in mermaid
    assert "Transformer" in mermaid
    assert "BERT" in mermaid


def test_to_mermaid_stats():
    """Mermaid 统计饼图"""
    graph = KnowledgeGraph()
    graph.add_paper("a", "A", ["NLP"])
    graph.add_paper("b", "B", ["NLP"])
    graph.add_edge("a", "b", "same_tag", "NLP")

    pie = to_mermaid_stats(graph)
    assert "pie" in pie
    assert "同标签" in pie


def test_export_graph_markdown():
    """导出完整图谱 Markdown"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 添加论文
        paper = ParsedPaper(
            title="Test Paper",
            year=2024,
            arxiv_id="test.001",
        )
        classify_and_store(paper, kb_path=tmpdir)

        # 导出图谱
        text = export_graph_markdown(tmpdir)
        assert "论文知识图谱" in text
        assert "统计" in text
        assert "Test Paper" in text

        # 验证 graph.md 存在
        graph_files = list(Path(tmpdir).glob("graph.md"))
        assert len(graph_files) == 1


def test_graph_stats():
    """图谱统计"""
    graph = KnowledgeGraph()
    graph.add_paper("a", "A", ["NLP"])
    graph.add_paper("b", "B", ["NLP"])
    graph.add_paper("c", "C", ["CV"])
    graph.add_edge("a", "b", "same_tag", "NLP")
    graph.add_edge("b", "c", "shared_concept", "model")

    stats = graph.stats()
    assert stats["total_papers"] == 3
    assert stats["total_edges"] == 2
    assert "same_tag" in stats["edge_types"]
    assert "shared_concept" in stats["edge_types"]
