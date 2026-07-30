"""测试 paper.py 数据模型。"""

from fool_paper.paper import (
    Author,
    ComplexityLevel,
    Formula,
    ParsedPaper,
    SafetyLevel,
    Section,
)


def test_paper_dataclass_basic():
    """测试 ParsedPaper 基本属性"""
    paper = ParsedPaper(
        title="Attention Is All You Need",
        authors=[Author(name="Vaswani et al.")],
        abstract="We propose a new simple network architecture...",
        year=2017,
        arxiv_id="1706.03762",
        total_pages=15,
        safety=SafetyLevel.SAFE,
        complexity=ComplexityLevel.MEDIUM,
    )
    assert paper.title == "Attention Is All You Need"
    assert paper.year == 2017
    assert paper.arxiv_id == "1706.03762"
    assert paper.safety == SafetyLevel.SAFE
    assert paper.complexity == ComplexityLevel.MEDIUM


def test_paper_with_sections():
    """测试 ParsedPaper 包含章节"""
    paper = ParsedPaper(
        title="Test Paper",
        sections=[
            Section(heading="Introduction", level=1, content="This is intro."),
            Section(heading="Method", level=1, content="Our method is..."),
            Section(
                heading="Attention Mechanism", level=2, content="We use attention."
            ),
        ],
    )
    assert len(paper.sections) == 3
    assert paper.sections[0].heading == "Introduction"
    assert paper.full_text.startswith("# Test Paper")
    assert "Attention Mechanism" in paper.full_text


def test_paper_with_formulas():
    """测试论文包含公式"""
    formula = Formula(
        id="(1)",
        latex=r"Attention(Q,K,V) = softmax(\frac{QK^T}{\sqrt{d_k}})V",
        section="Method",
    )
    paper = ParsedPaper(
        title="Test",
        formulas=[formula],
    )
    assert len(paper.formulas) == 1
    assert paper.formulas[0].latex.startswith(r"Attention")


def test_complexity_levels():
    """测试难度等级枚举"""
    assert ComplexityLevel.LOW.value == "low"
    assert ComplexityLevel.VERY_HIGH.value == "very_high"
    # 排序关系
    levels = [
        ComplexityLevel.LOW,
        ComplexityLevel.MEDIUM,
        ComplexityLevel.HIGH,
        ComplexityLevel.VERY_HIGH,
    ]
    assert all(isinstance(l, ComplexityLevel) for l in levels)


def test_safety_levels():
    """测试安全等级枚举"""
    assert SafetyLevel.SAFE.value == "safe"
    assert SafetyLevel.RESTRICTED.value == "restricted"
