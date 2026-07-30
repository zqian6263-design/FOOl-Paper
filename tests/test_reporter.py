"""测试 reporter.py — 报告生成。"""

from fool_paper.reporter import generate_report
from fool_paper.paper import (
    AnalysisResult,
    Author,
    ParsedPaper,
    Reference,
    Section,
)


def _make_sample_result() -> AnalysisResult:
    """创建一个示例分析结果用于测试。"""
    paper = ParsedPaper(
        title="Transformer",
        authors=[Author(name="Vaswani et al.")],
        abstract="We propose the Transformer model...",
        year=2017,
        arxiv_id="1706.03762",
        sections=[
            Section(heading="Introduction", level=1, content="Intro text."),
        ],
        references=[
            Reference(id="1", title="Seq2Seq", year=2014),
            Reference(id="2", title="Attention", year=2015),
        ],
        total_pages=15,
    )

    result = AnalysisResult(
        paper=paper,
        translation="### 📝 翻译\n\nWe propose the Transformer model...\n\n**中文**: 我们提出 Transformer 模型...",
        feynman="### 🧠 费曼拆解\n\n#### 一句话总结\nTransformer 是一种基于自注意力机制的序列建模架构。",
        innovation="### 💡 创新与不足\n\n#### 创新点\n...",
        replication="### 🔄 复现分析\n\n| 项目 | 状态 |\n|------|------|\n| 数据集 | ✅ |",
        tags=["NLP", "深度学习"],
        category="Natural Language Processing",
    )

    return result


def test_generate_full_report():
    """测试生成有所有分析结果的完整报告"""
    result = _make_sample_result()
    report = generate_report(result)

    # 应包含各部分
    assert result.paper.title in report
    assert "Transformer" in report
    assert "摘要" in report or "Abstract" in report
    assert "费曼" in report or "Feynman" in report
    assert "创新" in report
    assert "复现" in report or "Replication" in report
    assert "NLP" in report
    assert "FOOL-paper" in report


def test_generate_minimal_report():
    """测试生成最小报告（无分析结果）"""
    paper = ParsedPaper(
        title="Minimal Paper",
        sections=[Section(heading="Intro", level=1, content="Hello.")],
    )
    result = AnalysisResult(paper=paper)
    report = generate_report(result)

    assert "Minimal Paper" in report
    assert "我的思考" in report or "Thoughts" in report
    # 不应有 nil/None 等
    assert "None" not in report


def test_generate_report_with_tags_only():
    """测试只有标签的报告"""
    paper = ParsedPaper(title="Tagged Paper")
    result = AnalysisResult(paper=paper, tags=["CV", "GAN"])
    report = generate_report(result)

    assert "`CV`" in report
    assert "`GAN`" in report


def test_report_includes_references():
    """测试报告包含参考文献"""
    result = _make_sample_result()
    report = generate_report(result)

    assert "Seq2Seq" in report
    assert "Attention" in report


def test_report_includes_footer():
    """测试报告包含页脚"""
    result = _make_sample_result()
    report = generate_report(result)

    assert "FOOL-paper" in report
    assert "https://github.com/zqian6263-design/FOOl-Paper" in report
