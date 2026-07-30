"""测试 qa.py"""

from fool_paper.qa import ask_about_paper, search_paper, summarize_section
from fool_paper.paper import Author, ParsedPaper, Section


def _make_paper() -> ParsedPaper:
    return ParsedPaper(
        title="Transformer for NLP",
        authors=[Author(name="Smith"), Author(name="Jones")],
        abstract="We propose a new architecture based on attention mechanisms.",
        year=2023,
        sections=[
            Section(
                heading="Introduction",
                level=1,
                content="Attention mechanisms have become central to NLP. "
                "The key innovation is self-attention enabling parallel computation.",
            ),
            Section(
                heading="Method",
                level=1,
                content="Our method uses multi-head attention with 8 heads. "
                "Each head computes scaled dot-product attention independently.",
            ),
        ],
    )


def test_ask_about_paper():
    """测试问答 prompt 构建"""
    paper = _make_paper()
    prompt = ask_about_paper("What is self-attention?", paper)

    assert "Transformer for NLP" in prompt
    assert "Smith" in prompt
    assert "What is self-attention?" in prompt
    assert "章节结构" in prompt


def test_ask_with_context():
    """测试带上下文的问答"""
    paper = _make_paper()
    context = {
        "feynman": "The Transformer is like a parallel reader...",
        "innovation": "Key novelty: self-attention mechanism",
    }
    prompt = ask_about_paper("How does multi-head work?", paper, context)

    assert "已有分析" in prompt
    assert "parallel reader" in prompt


def test_search_paper_found():
    """搜索存在的关键词"""
    paper = _make_paper()
    results = search_paper("self-attention", paper)
    assert len(results) >= 1
    assert any("self-attention" in r["match_excerpt"].lower() for r in results)


def test_search_paper_not_found():
    """搜索不存在的关键词"""
    paper = _make_paper()
    results = search_paper("rocket science", paper)
    assert results == []


def test_search_paper_multiple():
    """搜索多处出现的关键词"""
    paper = _make_paper()
    results = search_paper("attention", paper, max_results=10)
    assert len(results) >= 2  # 摘要和 Introduction 都有


def test_summarize_section_found():
    """获取存在的章节"""
    paper = _make_paper()
    result = summarize_section(paper, "Method")
    assert "multi-head attention" in result


def test_summarize_section_not_found():
    """获取不存在的章节"""
    paper = _make_paper()
    result = summarize_section(paper, "Results")
    assert "未找到章节" in result
    assert "Introduction" in result  # 列出可用章节
