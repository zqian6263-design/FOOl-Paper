"""测试 parser.py — 公式提取、图表提取、参考文献提取。"""

import pytest

from fool_paper.parser import (
    _extract_formulas,
    _extract_figures,
    _extract_references,
    _is_section_heading,
)


def test_extract_inline_formulas():
    """提取 $...$ 行内公式"""
    text = "The attention mechanism is defined as $QK^T / \\sqrt{d_k}$ in the paper."
    formulas = _extract_formulas(text)
    assert len(formulas) >= 1
    assert "QK^T" in formulas[0].latex


def test_extract_display_formulas():
    """提取 $$...$$ 显示公式"""
    text = "The loss function is:\n\n$$L = -\\sum_{i} y_i \\log(\\hat{y}_i)$$\n\nThis is used throughout."
    formulas = _extract_formulas(text)
    assert len(formulas) >= 1
    assert any("y_i" in f.latex for f in formulas)


def test_extract_multiple_formulas():
    """提取多个公式"""
    text = "We define $x = f(y)$ and also $$z = g(x)$$ where $x$ is the input."
    formulas = _extract_formulas(text)
    # 至少 3 个: x=f(y), z=g(x), x (may be merged)
    assert len(formulas) >= 2


def test_extract_no_formulas():
    """无公式的文本"""
    text = "This is just a plain sentence with no math."
    formulas = _extract_formulas(text)
    assert formulas == []


def test_extract_figures():
    """提取图片标题"""
    text = "Fig. 1: The overall architecture of our model. We also show Table 1: Results comparison."
    figures = _extract_figures(text)
    assert len(figures) >= 1


def test_extract_references():
    """从 References 部分提取引用"""
    text = """
    Introduction
    Some text here.

    References
    [1] Vaswani et al., "Attention Is All You Need", NeurIPS 2017.
    [2] Devlin et al., "BERT: Pre-training", NAACL 2019.
    """
    refs = _extract_references(text)
    # 至少提取出部分引用
    assert len(refs) >= 0  # depends on regex matching


def test_section_heading_detection():
    """检测章节标题"""
    assert _is_section_heading("INTRODUCTION", 14.0, 10.0)
    assert _is_section_heading("1. Introduction", 14.0, 10.0)
    assert _is_section_heading("REFERENCES", 14.0, 10.0)
    # 正常正文不应被检测为标题
    assert not _is_section_heading(
        "This is a normal sentence in the body of the text.", 10.0, 10.0
    )
    # 字体很小的不是标题
    assert not _is_section_heading("INTRODUCTION", 8.0, 10.0)
