"""测试 organizer.py"""

import tempfile
from pathlib import Path

from fool_paper.organizer import (
    _auto_tag,
    _generate_paper_id,
    classify_and_store,
    get_kb_stats,
)
from fool_paper.paper import Author, ParsedPaper


def _make_paper() -> ParsedPaper:
    return ParsedPaper(
        title="Attention Is All You Need",
        authors=[Author(name="Vaswani et al.")],
        abstract="We propose the Transformer, a new simple network architecture based solely on attention mechanisms.",
        year=2017,
        arxiv_id="1706.03762",
    )


def test_auto_tag_transformer():
    """自动标记 Transformer 论文"""
    paper = _make_paper()
    tags = _auto_tag(paper)
    # Transformer 论文摘要匹配到 "Attention" 和 "Transformer"
    assert len(tags) >= 1
    assert "Attention" in tags or "Transformer" in tags


def test_auto_tag_nlp():
    """自动标记 NLP 论文"""
    paper = ParsedPaper(
        title="BERT for Text Classification",
        abstract="We fine-tune BERT, a large language model, on NLP tasks.",
    )
    tags = _auto_tag(paper)
    assert "语言模型" in tags or "自然语言处理" in tags


def test_auto_tag_empty_paper():
    """空论文应标记为需LLM推断"""
    paper = ParsedPaper(title="Unknown")
    tags = _auto_tag(paper)
    assert "需LLM推断" in tags


def test_generate_paper_id_arxiv():
    """arxiv 论文用 arxiv_id"""
    paper = _make_paper()
    paper_id = _generate_paper_id(paper)
    assert paper_id == "1706.03762"


def test_generate_paper_id_title():
    """无 arxiv_id 的论文用标题"""
    paper = ParsedPaper(title="My Custom Paper")
    paper_id = _generate_paper_id(paper)
    assert "my-custom-paper" in paper_id


def test_classify_and_store():
    """测试存入知识库"""
    paper = _make_paper()

    with tempfile.TemporaryDirectory() as tmpdir:
        path = classify_and_store(paper, kb_path=tmpdir)

        # 检查笔记文件存在
        note_path = Path(path)
        assert note_path.exists()

        # 检查内容
        content = note_path.read_text(encoding="utf-8")
        assert "Attention Is All You Need" in content
        assert "Vaswani" in content
        assert "2017" in content
        assert "1706.03762" in content
        assert "摘要" in content
        assert "我的思考" in content

        # 检查 frontmatter
        assert "---" in content
        assert "title:" in content
        assert "tags:" in content

        # 检查索引文件
        index_path = Path(tmpdir) / "index.md"
        assert index_path.exists()


def test_get_kb_stats():
    """测试知识库统计"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 空知识库
        stats = get_kb_stats(tmpdir)
        assert stats["total_papers"] == 0

        # 添加一篇论文
        paper1 = _make_paper()
        classify_and_store(paper1, kb_path=tmpdir)

        stats = get_kb_stats(tmpdir)
        assert stats["total_papers"] >= 1

        # 再添加一篇
        paper2 = ParsedPaper(
            title="BERT",
            abstract="Large language model for NLP.",
            arxiv_id="1810.04805",
        )
        classify_and_store(paper2, kb_path=tmpdir)

        stats = get_kb_stats(tmpdir)
        assert stats["total_papers"] >= 2
