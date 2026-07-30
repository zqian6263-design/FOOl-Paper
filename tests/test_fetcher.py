"""测试 fetcher.py — 来源检测逻辑。"""

from fool_paper.fetcher import _extract_arxiv_id, PaperSourceError, from_local_pdf
from fool_paper.paper import PaperSourceType


def test_extract_arxiv_id_from_url():
    """从完整 arxiv URL 提取 ID"""
    assert _extract_arxiv_id("https://arxiv.org/abs/1706.03762") == "1706.03762"
    assert _extract_arxiv_id("https://arxiv.org/abs/2306.12345v2") == "2306.12345"


def test_extract_arxiv_id_from_pdf_url():
    """从 arxiv PDF URL 提取 ID"""
    assert _extract_arxiv_id("https://arxiv.org/pdf/1706.03762.pdf") == "1706.03762"
    assert _extract_arxiv_id("https://arxiv.org/pdf/1706.03762v1.pdf") == "1706.03762"


def test_extract_arxiv_id_pure():
    """从纯 ID 提取"""
    assert _extract_arxiv_id("1706.03762") == "1706.03762"
    assert _extract_arxiv_id("arxiv:2306.12345") == "2306.12345"
    assert _extract_arxiv_id("2306.12345v3") == "2306.12345"


def test_extract_arxiv_id_in_text():
    """从文本中的 arxiv ID"""
    assert _extract_arxiv_id("读这篇 arxiv:1801.00001") == "1801.00001"


def test_extract_arxiv_id_returns_none():
    """非 arxiv 输入返回 None"""
    assert _extract_arxiv_id("hello world") is None
    assert _extract_arxiv_id("https://example.com/paper.pdf") is None
    assert _extract_arxiv_id("") is None


def test_from_local_pdf_not_found():
    """本地 PDF 不存在时报错"""
    try:
        from_local_pdf("/nonexistent/path/paper.pdf")
        assert False, "应该抛异常"
    except Exception as e:
        assert "不存在" in str(e) or "not found" in str(e).lower()
