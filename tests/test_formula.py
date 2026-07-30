"""测试 formula.py"""

from fool_paper.formula import (
    explain_formula,
    extract_symbols,
    formula_dependency_graph,
    trace_symbols,
    _analyze_structure,
)
from fool_paper.paper import Formula


def test_extract_attention_formula():
    """提取 Attention 公式符号"""
    latex = r"\text{Attention}(Q,K,V)=\text{softmax}(\frac{QK^T}{\sqrt{d_k}})V"
    symbols = extract_symbols(latex)

    assert "Q" in symbols
    assert "K" in symbols
    assert "V" in symbols
    assert "\\frac" in symbols
    assert "\\sqrt" in symbols
    assert "\\text" in symbols


def test_extract_greek_symbols():
    """提取希腊字母"""
    latex = r"L = -\sum_{i} y_i \log(\hat{y}_i) + \lambda \|\theta\|_2"
    symbols = extract_symbols(latex)

    assert "\\sum" in symbols
    assert "\\lambda" in symbols
    assert "\\theta" in symbols


def test_explain_formula():
    """测试公式解释"""
    formula = Formula(
        id="(1)",
        latex=r"\text{Attention}(Q,K,V)=\text{softmax}(\frac{QK^T}{\sqrt{d_k}})V",
        section="Method",
    )
    explanation = explain_formula(formula)
    assert "公式 (1)" in explanation
    assert "Attention" in explanation
    assert "符号说明" in explanation
    assert "结构分析" in explanation


def test_explain_formula_with_context():
    """测试带上下文的公式解释"""
    formula = Formula(
        id="(3)",
        latex=r"L_{CE} = -\sum_c y_c \log(p_c)",
        section="Training",
    )
    explanation = explain_formula(formula, context="We use cross-entropy loss for training.")
    assert "上下文" in explanation
    assert "cross-entropy" in explanation


def test_analyze_structure_fraction():
    """检测分数结构"""
    result = _analyze_structure(r"\frac{QK^T}{\sqrt{d_k}}")
    assert "分数" in result


def test_analyze_structure_summation():
    """检测求和结构"""
    result = _analyze_structure(r"\sum_{i=1}^{n} x_i")
    assert "求和" in result


def test_trace_symbols():
    """符号追踪"""
    f1 = Formula(id="(1)", latex=r"x = f(y)")
    f2 = Formula(id="(2)", latex=r"z = g(x)")
    formulas = [f1, f2]

    traced = trace_symbols(f2, formulas)
    assert "x" in traced
    assert "首次出现于公式 (1)" in traced["x"]


def test_dependency_graph():
    """公式依赖图"""
    f1 = Formula(id="(1)", latex=r"Q = X W_Q")
    f2 = Formula(id="(2)", latex=r"A = \text{softmax}(Q K^T)")
    f3 = Formula(id="(3)", latex=r"O = A V")

    edges = formula_dependency_graph([f1, f2, f3])
    # f2 依赖 f1 中定义的 Q
    assert any(e[0] == "(2)" and e[1] == "(1)" for e in edges)
