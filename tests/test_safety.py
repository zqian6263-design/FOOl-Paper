"""测试 safety.py"""

from fool_paper.safety import classify
from fool_paper.paper import ParsedPaper, SafetyLevel


def test_safe_paper():
    """常规论文标记为 SAFE"""
    paper = ParsedPaper(
        title="Training Neural Networks",
        abstract="We propose a new optimization method for deep learning.",
    )
    assert classify(paper) == SafetyLevel.SAFE


def test_restricted_paper():
    """涉及 weapons 的论文直接 RESTRICTED"""
    paper = ParsedPaper(
        title="Advanced AI",
        abstract="This paper discusses biological weapon detection methods.",
    )
    assert classify(paper) == SafetyLevel.RESTRICTED


def test_sensitive_paper():
    """涉及 surveillance 的论文 SENSITIVE"""
    paper = ParsedPaper(
        title="Computer Vision for Security",
        abstract="We present a mass surveillance system using deep learning.",
    )
    assert classify(paper) == SafetyLevel.SENSITIVE


def test_restricted_overrides_sensitive():
    """RESTRICTED 优先于 SENSITIVE"""
    paper = ParsedPaper(
        title="Military Application of AI",
        abstract="We analyze terrorism threats and surveillance systems.",
    )
    assert classify(paper) == SafetyLevel.RESTRICTED


def test_empty_paper():
    """空论文为 SAFE"""
    paper = ParsedPaper(title="")
    assert classify(paper) == SafetyLevel.SAFE


def test_nlp_paper_safe():
    """NLP 论文安全"""
    paper = ParsedPaper(
        title="BERT: Pre-training of Deep Bidirectional Transformers",
        abstract="We introduce a new language representation model called BERT.",
    )
    assert classify(paper) == SafetyLevel.SAFE
