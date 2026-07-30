"""测试 analyzer.py — prompt 构建。"""

import pytest

from fool_paper.analyzer import (
    analyze,
    build_prompts,
    feynman_deconstruction,
    first_principles_analysis,
    innovation_analysis,
    replication_analysis,
    translate_section,
)
from fool_paper.paper import (
    Author,
    ComplexityLevel,
    Formula,
    ParsedPaper,
    Reference,
    Section,
)


def _make_sample_paper() -> ParsedPaper:
    """创建一个示例论文用于测试。"""
    return ParsedPaper(
        title="Attention Is All You Need",
        authors=[Author(name="Vaswani"), Author(name="Shazeer")],
        abstract="We propose a new simple network architecture, the Transformer...",
        year=2017,
        arxiv_id="1706.03762",
        sections=[
            Section(
                heading="Introduction",
                level=1,
                content="Recent advances in sequence modeling have been dominated by...",
            ),
            Section(
                heading="Model Architecture",
                level=1,
                content="The Transformer follows an encoder-decoder structure...",
            ),
        ],
        formulas=[
            Formula(
                id="(1)",
                latex=r"\text{Attention}(Q,K,V) = \text{softmax}(\frac{QK^T}{\sqrt{d_k}})V",
            ),
        ],
        references=[
            Reference(id="1", title="Neural Machine Translation", year=2014),
            Reference(id="2", title="Layer Normalization", year=2016),
        ],
        total_pages=15,
        complexity=ComplexityLevel.MEDIUM,
    )


def test_build_prompts_all_tasks():
    """测试构建所有任务的 prompt"""
    paper = _make_sample_paper()
    tasks = ["translate", "feynman", "first_principles", "innovation", "replication"]
    prompts = build_prompts(paper, tasks)

    assert len(prompts) == 5
    for task in tasks:
        assert task in prompts
        assert len(prompts[task]) > 200  # prompt 应该有一定长度
        assert paper.title in prompts[task]  # 论文标题应出现在 prompt 中
        assert paper.abstract.strip()[:30] in prompts[task]  # 摘要应出现在 prompt 中


def test_build_prompts_single_task():
    """测试构建单个任务的 prompt"""
    paper = _make_sample_paper()
    prompts = build_prompts(paper, ["feynman"])
    assert len(prompts) == 1
    assert "feynman" in prompts
    assert "费曼" in prompts["feynman"] or "Feynman" in prompts["feynman"]


def test_analyze_returns_built_prompts():
    """测试 analyze() 返回构建好的 prompt"""
    paper = _make_sample_paper()
    results = analyze(paper, ["feynman", "innovation"])
    assert len(results) == 2
    assert "feynman" in results
    assert "innovation" in results


def test_invalid_task_raises():
    """未知任务名应抛出 ValueError"""
    paper = _make_sample_paper()
    with pytest.raises(ValueError):
        build_prompts(paper, ["unknown_task"])


def test_convenience_functions():
    """测试便捷函数"""
    paper = _make_sample_paper()

    prompt = feynman_deconstruction(paper)
    assert len(prompt) > 200
    assert paper.title in prompt

    prompt = first_principles_analysis(paper)
    assert len(prompt) > 200

    prompt = innovation_analysis(paper)
    assert len(prompt) > 200

    prompt = replication_analysis(paper)
    assert len(prompt) > 200

    prompt = translate_section(paper)
    assert len(prompt) > 200


def test_low_complexity_short_paper():
    """短论文的 prompt 应该较短"""
    paper = ParsedPaper(
        title="Short Note",
        sections=[Section(heading="Method", level=1, content="A simple method.")],
        total_pages=2,
        complexity=ComplexityLevel.LOW,
    )
    prompt = feynman_deconstruction(paper)
    assert len(prompt) > 50  # 至少有些内容
